"""Flag sustained household electricity outliers with a rolling robust z-score."""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--input",required=True);p.add_argument("--date","--date-column",dest="date",default="Date");p.add_argument("--time",default="Time");p.add_argument("--value",default="Global_active_power");p.add_argument("--threshold",type=float,default=6.0);p.add_argument("--out",default="outputs");a=p.parse_args()
 d=pd.read_csv(a.input,sep=";",na_values=["?"],low_memory=False)
 d["timestamp"]=pd.to_datetime(d[a.date].astype(str)+" "+d[a.time].astype(str),dayfirst=True,errors="coerce");d[a.value]=pd.to_numeric(d[a.value],errors="coerce")
 s=d.dropna(subset=["timestamp",a.value]).set_index("timestamp")[a.value].resample("5min").mean().dropna()
 med=s.rolling("6h",min_periods=24,center=False).median();mad=(s-med).abs().rolling("6h",min_periods=24).median().replace(0,np.nan)
 z=.6745*(s-med)/mad;events=pd.DataFrame({"value":s,"robust_z":z}).assign(alert=lambda x:x.robust_z.abs()>=a.threshold).dropna()
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True);events[events.alert].to_csv(out/"anomaly_events.csv");report={"input_rows":len(d),"resampled_points":len(s),"alerts":int(events.alert.sum()),"threshold":a.threshold,"method":"trailing 6-hour rolling median/MAD after 5-minute resampling"}
 (out/"summary.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=="__main__":main()
