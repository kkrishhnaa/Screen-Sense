import pandas as pd
import numpy as np
from collections import Counter
from typing import Dict, List, Any

class RecommendationEngine:
    def __init__(self, csv_path: str):
        print("DEBUG: Starting CSV load...")
        self.df_reco = pd.read_csv(csv_path)
        print(f"DEBUG: CSV loaded, shape: {self.df_reco.shape}")
        
        # Fill NaN and convert types (safe for your data)
        self.df_reco['Gender'] = self.df_reco['Gender'].fillna('Unknown').astype(str)
        self.df_reco['Primary_Device'] = self.df_reco['Primary_Device'].fillna('Unknown').astype(str)
        self.df_reco['Health_Impacts'] = self.df_reco['Health_Impacts'].fillna('None').astype(str)
        self.df_reco['Urban_or_Rural'] = self.df_reco['Urban_or_Rural'].fillna('Urban').astype(str)
        self.df_reco['Avg_Daily_Screen_Time_hr'] = pd.to_numeric(self.df_reco['Avg_Daily_Screen_Time_hr'], errors='coerce').fillna(5.0)
        self.df_reco['Educational_to_Recreational_Ratio'] = pd.to_numeric(self.df_reco['Educational_to_Recreational_Ratio'], errors='coerce').fillna(1.0)
        self.df_reco['Age'] = pd.to_numeric(self.df_reco['Age'], errors='coerce').fillna(12).astype(int)
        # Use pre-computed if available, else calculate
        if 'Estimated_Recreational_hr' in self.df_reco.columns:
            print("DEBUG: Using pre-computed estimated hours")
        else:
            print("DEBUG: Calculating estimated hours...")
            self.df_reco['Estimated_Recreational_hr'] = self.df_reco.apply(
                lambda r: r['Avg_Daily_Screen_Time_hr'] / (1 + r['Educational_to_Recreational_Ratio'])
                if r['Educational_to_Recreational_Ratio'] >= 0 else np.nan, axis=1)
            self.df_reco['Estimated_Educational_hr'] = self.df_reco['Avg_Daily_Screen_Time_hr'] - self.df_reco['Estimated_Recreational_hr']
        # Threshold (use pre-computed if available)
        if 'Threshold_Limit_hr' in self.df_reco.columns:
            print("DEBUG: Using pre-computed threshold")
        else:
            def age_threshold(age):
                if age <= 10:
                    return 2.0
                elif age <= 14:
                    return 4.0
                else:
                    return 6.0
            self.df_reco['Threshold_Limit_hr'] = self.df_reco['Age'].apply(age_threshold)
        print("DEBUG: Data prep done")

        # Drop invalid rows
        self.df_reco = self.df_reco.dropna(subset=['Age', 'Gender', 'Primary_Device'])
        print(f"DEBUG: After dropna, shape: {self.df_reco.shape}")

        print("DEBUG: Starting groupby...")
        self.recom_df2 = self.df_reco.groupby(['Age', 'Gender', 'Primary_Device']).agg(
            Threshold_Limit_hr=('Threshold_Limit_hr', 'mean'),
            Avg_screen_time_per_criterias=('Avg_Daily_Screen_Time_hr', 'mean'),
            Avg_Daily_Screen_Time_per_age_only=('Avg_Daily_Screen_Time_hr', 'mean'),
            Avg_Educational_Screen_time=('Estimated_Educational_hr', 'mean'),
            Avg_Recreational_Screen_time=('Estimated_Recreational_hr', 'mean'),
            Educational_to_Recreational_Ratio=('Educational_to_Recreational_Ratio', 'mean'),
        ).reset_index()
        print(f"DEBUG: Groupby done, recom_df2 shape: {self.recom_df2.shape}")

        print("DEBUG: Starting health impacts processing...")
        health_df = self.df_reco[['Age', 'Primary_Device', 'Health_Impacts']].copy()
        health_df['Health_Impacts'] = health_df['Health_Impacts'].str.replace(' ', '')
        health_exploded = health_df.assign(Health_Impact=health_df['Health_Impacts'].str.split(',')).explode('Health_Impact')
        self.Health_Impacts_count_df = (health_exploded
                                        .groupby(['Age', 'Primary_Device', 'Health_Impact'])
                                        .size()
                                        .reset_index(name='Health_Impact_Count'))
        print(f"DEBUG: Health impacts done, shape: {self.Health_Impacts_count_df.shape}")

        self.top_health_impacts_for_group = self._top_health_impacts_for_group
        self.device_health_profile = self._compute_device_health_profile()
        print("DEBUG: Engine init complete!")

    def _top_health_impacts_for_group(self, age, gender, device, topn=3):
        grp = self.df_reco[(self.df_reco['Age'] == age) & (self.df_reco['Primary_Device'] == device)]
        if grp.empty:
            return []
        cnt = Counter(','.join(grp['Health_Impacts'].fillna('None')).replace(' ', '').split(','))
        if '' in cnt: del cnt['']
        top = [k for k, v in cnt.most_common(topn)]
        return top

    def _compute_device_health_profile(self):
        if self.Health_Impacts_count_df.empty:
            return {"Smartphone": 0.45, "Laptop": 0.2, "TV": 0.35, "Tablet": 0.3}
        dev_sum = self.Health_Impacts_count_df.groupby('Primary_Device')['Health_Impact_Count'].sum()
        max_count = dev_sum.max()
        profile = {dev: count / max_count if max_count > 0 else 0 for dev, count in dev_sum.items()}
        for dev in ["Smartphone", "Laptop", "TV", "Tablet"]:
            if dev not in profile:
                profile[dev] = 0.5
        return profile

    def generate_insights(self, user_data: Dict[str, Any], total_hours: float) -> Dict[str, Any]:
        print(f"DEBUG: Generating insights for age {user_data['age']}")
        age = int(user_data["age"])
        gender = user_data["gender"].capitalize()
        device = user_data["primary_device"].capitalize()
        edu_time = float(user_data["educational_hours"])
        rec_time = float(user_data["recreational_hours"])
        health_impacts = user_data.get("health_impacts", "")
        urban_or_rural = user_data.get("urban_or_rural", "Urban")

        screen_time = edu_time + rec_time
        report_lines = []

        # Find exact match
        match = self.recom_df2[
            (self.recom_df2['Age'] == age) &
            (self.recom_df2['Gender'] == gender) &
            (self.recom_df2['Primary_Device'] == device)
        ]
        if match.empty:
            # Fallback to age-only
            age_grp = self.recom_df2[self.recom_df2['Age'] == age]
            if not age_grp.empty:
                row = age_grp.iloc[0]
                report_lines.append(f"Note: Using age-based averages (no exact {gender}/{device} match in data).")
            else:
                # Ultimate fallback: Hardcoded defaults
                def age_threshold(age):
                    if age <= 10:
                        return 2.0
                    elif age <= 14:
                        return 4.0
                    else:
                        return 6.0
                limit = age_threshold(age)
                avg_detailed = self.df_reco['Avg_Daily_Screen_Time_hr'].mean()
                avg_age_only = avg_detailed
                avg_edu_age = self.df_reco['Estimated_Educational_hr'].mean() if 'Estimated_Educational_hr' in self.df_reco.columns else 2.5
                avg_rec_age = self.df_reco['Estimated_Recreational_hr'].mean() if 'Estimated_Recreational_hr' in self.df_reco.columns else 2.5
                avg_ratio_age = self.df_reco['Educational_to_Recreational_Ratio'].mean()
                report_lines.append(f"Note: Using global averages (limited data for age {age}).")
                row = pd.DataFrame({
                    'Threshold_Limit_hr': [limit],
                    'Avg_screen_time_per_criterias': [avg_detailed],
                    'Avg_Daily_Screen_Time_per_age_only': [avg_age_only],
                    'Avg_Educational_Screen_time': [avg_edu_age],
                    'Avg_Recreational_Screen_time': [avg_rec_age],
                    'Educational_to_Recreational_Ratio': [avg_ratio_age]
                }).iloc[0]
        else:
            row = match.iloc[0]

        # Extract values
        limit = float(row['Threshold_Limit_hr'])
        avg_detailed = float(row['Avg_screen_time_per_criterias'])
        avg_age_only = float(row['Avg_Daily_Screen_Time_per_age_only'])
        avg_edu_age = float(row['Avg_Educational_Screen_time'])
        avg_rec_age = float(row['Avg_Recreational_Screen_time'])
        avg_ratio_age = float(row['Educational_to_Recreational_Ratio'])

        exceeded = screen_time > limit
        exceeded_by = max(0, screen_time - limit)

        # Report lines (your original logic)
        report_lines.append(f"Entered Age: {age}, Gender: {gender}, Device: {device}")
        report_lines.append(f"Educational hrs: {edu_time:.2f}, Recreational hrs: {rec_time:.2f}, Total: {screen_time:.2f} hrs")
        if exceeded:
            report_lines.append(f"⚠️ You exceed the recommended limit of {limit:.2f} hrs by {exceeded_by:.2f} hrs.")
        else:
            report_lines.append(f"✅ Within recommended limit ({limit:.2f} hrs) for your group.")

        diff_hr = screen_time - avg_detailed
        diff_pct = (diff_hr / avg_detailed) * 100 if avg_detailed != 0 else 0
        if diff_hr > 0:
            report_lines.append(f"Your usage is {diff_hr:.2f} hrs ({diff_pct:.1f}%) above avg for similar peers.")
        elif diff_hr < 0:
            report_lines.append(f"Your usage is {abs(diff_hr):.2f} hrs ({abs(diff_pct):.1f}%) below avg for similar peers.")
        else:
            report_lines.append("Your usage matches the avg for similar peers.")

        diff_age_hr = screen_time - avg_age_only
        diff_age_pct = (diff_age_hr / avg_age_only) * 100 if avg_age_only != 0 else 0
        if diff_age_hr > 0:
            report_lines.append(f"Compared to avg for age {age}, you are {diff_age_hr:.2f} hrs ({diff_age_pct:.1f}%) higher.")
        elif diff_age_hr < 0:
            report_lines.append(f"Compared to avg for age {age}, you are {abs(diff_age_hr):.2f} hrs ({abs(diff_age_pct):.1f}%) lower.")
        else:
            report_lines.append("You match the age group average exactly.")

        edu_diff_hr = edu_time - avg_edu_age
        edu_diff_pct = (edu_diff_hr / avg_edu_age) * 100 if avg_edu_age != 0 else 0
        if edu_diff_hr > 0:
            report_lines.append(f"Educational time is {edu_diff_hr:.2f} hrs ({edu_diff_pct:.1f}%) higher than peers.")
        elif edu_diff_hr < 0:
            report_lines.append(f"Educational time is {abs(edu_diff_hr):.2f} hrs ({abs(edu_diff_pct):.1f}%) lower than peers.")

        rec_diff_hr = rec_time - avg_rec_age
        rec_diff_pct = (rec_diff_hr / avg_rec_age) * 100 if avg_rec_age != 0 else 0
        if rec_diff_hr > 0:
            report_lines.append(f"Recreational time is {rec_diff_hr:.2f} hrs ({rec_diff_pct:.1f}%) higher than peers.")
        elif rec_diff_hr < 0:
            report_lines.append(f"Recreational time is {abs(rec_diff_hr):.2f} hrs ({abs(rec_diff_pct):.1f}%) lower than peers.")

        if rec_time != 0:
            user_ratio = edu_time / rec_time
            report_lines.append(f"Your Educational:Recreational ratio = {user_ratio:.3f} (group avg = {avg_ratio_age:.3f})")
            diff_ratio = user_ratio - avg_ratio_age
            if diff_ratio > 0:
                report_lines.append("You focus more on educational content than peers.")
            elif diff_ratio < 0:
                report_lines.append("You focus more on recreational content than peers.")
        else:
            report_lines.append("No recreational time reported (ratio = ∞).")

        top_impacts = self.top_health_impacts_for_group(age, gender, device, topn=3)
        if top_impacts:
            report_lines.append("Most common health impacts among similar users: " + ", ".join(top_impacts))
            if exceeded:
                report_lines.append("Exceeding time in this group is often linked to: " + ", ".join(top_impacts))
        else:
            report_lines.append("No sufficient health-impact data for this group.")

        exceed_pct = ((screen_time - limit) / limit) * 100
        if exceed_pct <= 0:
            risk = "Healthy"
        elif exceed_pct <= 20:
            risk = "Mild Risk"
        elif exceed_pct <= 50:
            risk = "High Risk"
        else:
            risk = "Severe Risk"
        report_lines.append(f"Risk Level: {risk}")

        devices_for_age = self.Health_Impacts_count_df[self.Health_Impacts_count_df['Age'] == age]
        if not devices_for_age.empty:
            dev_sum = (devices_for_age.groupby('Primary_Device')['Health_Impact_Count'].sum().reset_index(name='Health_Impacts_count'))
            best_row = dev_sum.loc[dev_sum['Health_Impacts_count'].idxmin()]
            best_device = best_row['Primary_Device']
            best_count = int(best_row['Health_Impacts_count'])
            report_lines.append(f"Device with fewest reported health issues for age {age}: {best_device} ({best_count} cases).")
            if device != best_device:
                report_lines.append(f"Consider switching from {device} to {best_device} for potentially healthier usage.")
        else:
            report_lines.append("No sufficient device-health data to recommend a device for your age.")

        # New: Use Urban_or_Rural for rec
        if urban_or_rural.lower() == "rural":
            report_lines.append("Tip for Rural users: Incorporate outdoor activities to balance screen time.")

        if health_impacts:
            report_lines.append(f"Note: Reported health impacts ({health_impacts})—consider consulting a doctor.")

        print("DEBUG: Insights generated!")

        return {
            "exceeded": exceeded,
            "recommendations": report_lines,
            "details": {
                "recommended_limit": round(limit, 1),
                "total_screen_time": round(screen_time, 1),
                "exceeded_by": round(exceeded_by, 1),
                "peer_averages": {
                    "age": round(avg_age_only, 1),
                    "gender": round(avg_detailed, 1),
                    "device": round(avg_detailed, 1),
                },
                "device_health_profile": self.device_health_profile,
            },
            "risk": risk
        }