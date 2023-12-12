from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

# from app.src.core.schemas.responses.get_leads_response import GetLeadsResponse
from app.src.core.services.lead_service import LeadService
from app.src.core.schemas.requests.create_lead_request import CreateLeadRequestModel
from app.src.core.schemas.responses.create_lead_response import CreateLeadResponseModel
from app.src.core.schemas.responses.create_lead_type_response import CreateLeadTypeResponseModel
from app.src.core.schemas.requests.create_lead_type_request import CreateLeadTypeRequestModel
from app.src.core.schemas.responses.lead_info_response import LeadInfoResponse

lead_router = APIRouter(tags=['Lead'])


@lead_router.post(
    "/create-lead",
    summary="Create lead card in callensights",
    response_model=CreateLeadResponseModel,
    response_model_by_alias=False
)
async def create_lead(
        lead_input: CreateLeadRequestModel,
        lead_service: LeadService = Depends()
) -> JSONResponse:
    response = lead_service.create_lead(lead_input)
    return JSONResponse(content=response)


@lead_router.post(
    "/create-lead-type",
    summary="Define a new type of lead",
    response_model=CreateLeadTypeResponseModel,
    response_model_by_alias=False
)
async def create_lead_type(
        lead_type_input: CreateLeadTypeRequestModel,
        lead_service: LeadService = Depends()
) -> JSONResponse:
    response = lead_service.create_lead_type(lead_type_input)
    return JSONResponse(content=response)


@lead_router.get(
    "/info",
    summary="Get list of leads assigned to a rep or unassigned",
    response_model=LeadInfoResponse,
    response_model_by_alias=False
)
async def lead_info(
        lead_id: int,
        user_id: str,
        lead_service: LeadService = Depends()
) -> JSONResponse:
    response = lead_service.get_lead_info(lead_id, user_id)
    return JSONResponse(content=response)


@lead_router.patch(
    "/update-lead-stage",
    summary="Update stage of the user",
    response_model_by_alias=False
)
async def update_lead_stage(
        lead_id: int,
        user_id: str,
        lead_service: LeadService = Depends()
) -> JSONResponse:
    status = lead_service.update_stage(lead_id, user_id)
    return JSONResponse(content=status)

# @lead_router.get(
#     "/get-leads",
#     summary="Get all available leads",
#     response_model=GetLeadsResponse,
#     response_model_by_alias=False
# )
# def get_loads(
#         lead_service: LeadService = Depends()
# ) -> JSONResponse:
#     leads = lead_service.get_leads