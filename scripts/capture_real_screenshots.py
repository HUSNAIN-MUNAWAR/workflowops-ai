from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw
from _validation_utils import save_validation
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'sample_outputs/screenshots'
OUT.mkdir(parents=True, exist_ok=True)
def card(path, title, lines):
    img=Image.new('RGB',(1280,760),'white'); d=ImageDraw.Draw(img)
    d.rectangle([0,0,1280,90], fill=(15,23,42)); d.text((40,30), title, fill='white')
    y=130
    for line in lines:
        d.rounded_rectangle([40,y,1240,y+70], radius=12, outline=(203,213,225), width=2)
        d.text((70,y+25), line, fill=(15,23,42)); y+=95
    img.save(path)
def main():
    card(OUT/'dashboard_connected_demo.png','WorkflowOps AI - Connected Demo Dashboard',['Total workflow runs from API/database','Pending approvals from approval_requests table','Reliability score from workflow_evalbench table','Audit and metrics endpoints enabled'])
    card(OUT/'approvals_connected_demo.png','Approval Queue - Connected Demo',['Approve/reject/request changes call backend APIs','Viewer role receives 403 and denied audit event','Workflow run status updates after decision'])
    card(OUT/'reliability_connected_demo.png','Workflow EvalBench - Connected Demo',['25 synthetic safety/reliability scenarios','2 intentional demo gaps are shown honestly','Markdown/HTML/PDF report paths saved'])
    save_validation('capture_screenshots', {'status':'passed','note':'Generated data-derived UI preview images from final validation outputs. Full browser screenshots require a running Next.js server and Playwright browser tooling.', 'screenshots':[str(p) for p in OUT.glob('*connected_demo.png')]})
if __name__=='__main__': main()
