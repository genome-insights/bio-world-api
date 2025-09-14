from fastapi import APIRouter

from app.schemas.bioanalysis import BioAnalysisIn

router = APIRouter(prefix="/bioanalysis", tags=["bcr_abl"])

@router.post("/", summary="Run BCR-ABL analysis")
def run_bcr_abl(payload: BioAnalysisIn):
    return payload
