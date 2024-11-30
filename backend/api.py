from flask_restful import Resource, Api
from flask import request
from .models import *
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib
matplotlib.use('agg')

api=Api()


class Apistatistics(Resource):
    def get(self):
        status_count=request.json.get("status_count")
        cu=request.json.get("cu")
        m=request.json.get("m")
        specific=request.json.get("specific")
        labels = list(status_count.keys())
        sizes = list(status_count.values())
        total = sum(sizes)
        savefile=f"/static/{cu}/statistics/service_plan_distribution.png"
        if total!=0:
            
            colors = sns.color_palette("pastel", len(labels))
            fig, ax = plt.subplots(figsize=(8, 6))
            wedges, _ = ax.pie(
                sizes,
                startangle=140,
                colors=colors,
                textprops=dict(color="black")
            )

            # Add legend with status and percentage
            legend_labels = [f"{label}: {count}" for label, count in zip(labels, sizes)]
            ax.legend(
                wedges, legend_labels, title="Booking Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1)
            )

            if m=="GET": 
                ax.set_title("Status-wise Distribution of Bookings", fontsize=14, pad=20)
            else:
                if cu=="professional":
                    ax.set_title(f"Status-wise Distribution of Bookings for {specific}", fontsize=14, pad=20)
                elif cu=="admin":
                    ax.set_title(f"Status-wise Distribution of Bookings for {specific}", fontsize=14, pad=20)

            # Modern aesthetics
            plt.tight_layout()
            sns.set_theme(style="whitegrid")
            
            plt.savefig(f".{savefile}", dpi=300, bbox_inches='tight')
            plt.clf()
            return {"message":"Summary for Professional created Successfully","path":savefile},200
        else:
            print("total is not 0")
            return {"message":"No Data to show","path":"Not available"},204
        
    

api.add_resource(Apistatistics,"/api/extractstats")