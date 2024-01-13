from enum import Enum


class MediaRouterPaths(Enum):
    PREFIX = "/media"

    UPLOAD = "/upload"
    GET_UPLOADS = "/get-uploads"
    GET_MEDIA = "/get-media"
    GET_FEEDBACK = "/get-feedback"
    GET_TRANSCRIPT = "/get-transcript"


class LeadRouterPaths(Enum):
    PREFIX = "/lead"

    CREATE_LEAD = "/create-lead"
    CREATE_LEAD_TYPE = "/create-lead-type"
    LEAD_INFO = "/info"
    UPDATE_LEAD_STAGE = "/update-lead-stage"
    ASSIGN_TO = "/assign_to"
    ADD_COMMENT = "/add-comment"


class UserRouterPaths(Enum):
    PREFIX = "/user"

    WORKSPACE = "/workspace"
