from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import ForeignKey
from datetime import datetime, date

Base = declarative_base()


class UserGroup(Base):
    __tablename__ = "cns_user_group"

    id: Mapped[int] = mapped_column('ug_group_id', primary_key=True)
    group_name: Mapped[str] = mapped_column('ug_group_name', nullable=False, unique=True)
    group_desc: Mapped[str] = mapped_column('ug_group_desc')
    created_dt: Mapped[datetime] = mapped_column('ug_created_dt', default=datetime.now())
    end_dt: Mapped[datetime] = mapped_column('ug_end_dt')

    def __repr__(self) -> str:
        return f"UserGroup(id={self.id}, group_name={self.group_name})"


class User(Base):
    __tablename__ = "cns_user_def"

    id: Mapped[int] = mapped_column('cu_user_id', primary_key=True)
    clerk_id: Mapped[str] = mapped_column('cu_clerk_user_id', unique=True)
    user_name: Mapped[str] = mapped_column('cu_user_name')
    first_name: Mapped[str] = mapped_column('cu_first_name')
    middle_name: Mapped[str] = mapped_column('cu_middle_name')
    last_name: Mapped[str] = mapped_column('cu_last_name')
    email: Mapped[str] = mapped_column('cu_email')
    phone: Mapped[str] = mapped_column('cu_ph')
    organization: Mapped[str] = mapped_column('cu_organization')
    role: Mapped[str] = mapped_column('cu_role')
    created_dt: Mapped[datetime] = mapped_column('cu_created_dt', default=datetime.now())
    updated_dt: Mapped[datetime] = mapped_column('cu_updated_dt')
    image_url: Mapped[str] = mapped_column("cu_image_url")
    user_group: Mapped[int] = mapped_column(
        'cu_user_group_id',
        ForeignKey('cns_user_group.ug_group_id'),
        nullable=False
    )
    manager_id: Mapped[int] = mapped_column(
        "cu_manager_id",
        ForeignKey("cns_user_def.cu_user_id"),
        nullable=True
    )


class Media(Base):
    __tablename__ = "cns_media_def"

    id: Mapped[int] = mapped_column('cm_media_id', primary_key=True)
    media_code: Mapped[str] = mapped_column('cm_media_code', unique=True)
    # user_id: Mapped[int] = mapped_column() # Put reference here
    user_id: Mapped[int] = mapped_column('cm_user_id', ForeignKey('cns_user_def.cu_user_id'), nullable=False)
    original_name: Mapped[str] = mapped_column('cm_original_name')
    file_type: Mapped[str] = mapped_column('cm_file_type')
    stored_file: Mapped[str] = mapped_column('cm_store_file')
    media_len: Mapped[int] = mapped_column('cm_media_length')
    media_size: Mapped[int] = mapped_column('cm_media_size')
    bucket: Mapped[str] = mapped_column('cm_bucket')
    event_date: Mapped[datetime] = mapped_column('cm_event_dt')
    rep_name: Mapped[str] = mapped_column('cm_rep_name')
    is_uploaded: Mapped[bool] = mapped_column('cm_is_uploaded', nullable=False, default=False)
    # lead_name: Mapped[str] = mapped_column('cm_lead_name')
    # lead_type: Mapped[str] = mapped_column('cm_lead_type')
    conv_type: Mapped[str] = mapped_column('cm_conv_type')
    demography: Mapped[str] = mapped_column('cm_demography')
    lang_code: Mapped[str] = mapped_column('cm_lang_code')
    product: Mapped[str] = mapped_column('cm_product')
    lead_id: Mapped[str] = mapped_column('cm_lead_id')


class MediaStatus(Base):
    __tablename__ = "cns_media_status"

    id: Mapped[int] = mapped_column('ms_status_id', primary_key=True, autoincrement="auto")
    # media_id # Put reference here
    media_id: Mapped[int] = mapped_column('ms_media_id', ForeignKey('cns_media_def.cm_media_id'), nullable=False)
    trans_status_cd: Mapped[str] = mapped_column('ms_trans_status_cd', default='N')
    trans_start_dt: Mapped[datetime] = mapped_column('ms_trans_start_dt')
    trans_end_dt: Mapped[datetime] = mapped_column('ms_trans_end_dt')

    fedbk_status_cd: Mapped[str] = mapped_column('ms_fedbk_status_cd', default='N')
    fedbk_start_dt: Mapped[datetime] = mapped_column('ms_fedbk_start_dt')
    fedbk_end_dt: Mapped[datetime] = mapped_column('ms_fedbk_end_dt')

    comments: Mapped[str] = mapped_column('ms_comments')
    stage_inputs: Mapped[str] = mapped_column('ms_stage_inputs')


class ApplicationConfig(Base):
    __tablename__ = "cns_application_config"

    id: Mapped[int] = mapped_column('ac_config_id', primary_key=True)
    config_key: Mapped[str] = mapped_column('ac_config_key', unique=True)
    config_value: Mapped[str] = mapped_column('ac_config_value')
    config_desc: Mapped[str] = mapped_column('ac_config_desc')
    created_dt: Mapped[datetime] = mapped_column('ac_created_dt', default=datetime.now())
    updated_dt: Mapped[datetime] = mapped_column('ac_updated_dt')


class GroupMessages(Base):
    __tablename__ = "cns_group_message"

    id: Mapped[int] = mapped_column('gm_msg_id', primary_key=True)
    # group_id # Put reference here
    group_id: Mapped[int] = mapped_column('gm_group_id', ForeignKey('UserGroup.id'), nullable=False)
    msg_order: Mapped[int] = mapped_column('gm_msg_order')
    message: Mapped[str] = mapped_column('gm_message')
    msg_status: Mapped[str] = mapped_column('gm_msg_status')
    created_dt: Mapped[datetime] = mapped_column('gm_created_dt', default=datetime.now())
    end_dt: Mapped[datetime] = mapped_column('gm_end_dt')


class LeadStages(Base):
    __tablename__ = "cns_lead_stage_def"

    id: Mapped[int] = mapped_column('ls_stage_id', primary_key=True)
    code: Mapped[str] = mapped_column('ls_stage_code')
    description: Mapped[str] = mapped_column('ls_stage_desc')
    is_active: Mapped[bool] = mapped_column('ls_is_active')
    created_dt: Mapped[datetime] = mapped_column('ls_created_dt', default=datetime.now())
    modified_dt: Mapped[datetime] = mapped_column('ls_modified_dt')


class LeadCallMetrics(Base):
    __tablename__ = "cns_lead_call_metrics"

    id: Mapped[int] = mapped_column('lcm_id', primary_key=True)

    lead_type_id: Mapped[int] = mapped_column('lcm_lead_type_id', ForeignKey('cns_lead_types_def.lt_type_id'), nullable=False)
    call_type_id: Mapped[int] = mapped_column('lcm_call_type_id', ForeignKey('cns_lead_stage_def.ls_stage_id'), nullable=False)
    metrics_id: Mapped[int] = mapped_column('lcm_metrics_id', ForeignKey('cns_metrics_def.md_metric_id'), nullable=False)

    lcm_created_dt: Mapped[datetime] = mapped_column('lcm_created_dt', default=datetime.now())


class Lead(Base):
    __tablename__ = "cns_lead_def"

    id: Mapped[int] = mapped_column('cl_lead_id', primary_key=True)
    name: Mapped[str] = mapped_column('cl_lead_name')
    email: Mapped[str] = mapped_column('cl_email')
    phone: Mapped[str] = mapped_column('cl_phone', unique=True)
    country: Mapped[str] = mapped_column('cl_country', nullable=True)
    st_province: Mapped[str] = mapped_column('cl_state_province', nullable=True)
    stage_id: Mapped[int] = mapped_column("cl_stage_id", ForeignKey('cns_lead_stage_def.ls_stage_id'), nullable=True)
    assigned_to: Mapped[int] = mapped_column("cl_assigned_to", ForeignKey('cns_user_def.cu_user_id'), nullable=True)
    lead_desc: Mapped[str] = mapped_column("cl_lead_desc")
    created_dt: Mapped[datetime] = mapped_column('cl_created_dt', default=datetime.now())
    updated_dt: Mapped[datetime] = mapped_column('cl_updated_dt')
    lead_type_code: Mapped[str] = mapped_column('cl_type_code', nullable=False)


class LeadTypes(Base):
    __tablename__ = "cns_lead_types_def"

    id: Mapped[int] = mapped_column('lt_type_id', primary_key=True)
    name: Mapped[str] = mapped_column('lt_type_name')
    description: Mapped[str] = mapped_column('lt_type_desc')

    created_dt: Mapped[datetime] = mapped_column('lt_created_dt', default=datetime.now())
    code: Mapped[str] = mapped_column('lt_type_code', nullable=False)


class Metrics(Base):
    __tablename__ = "cns_metrics_def"

    id: Mapped[int] = mapped_column('md_metric_id', primary_key=True)
    title: Mapped[str] = mapped_column('md_metric_title')
    prompt: Mapped[str] = mapped_column('md_metric_prompt')
    key_metric: Mapped[str] = mapped_column('md_key_metric', default='N')

    created_dt: Mapped[datetime] = mapped_column('md_created_dt', default=datetime.now())
    updated_dt: Mapped[datetime] = mapped_column('md_updated_dt')


class Activity(Base):
    __tablename__ = "cns_activity"

    id: Mapped[int] = mapped_column("ca_activity_id", primary_key=True)
    done_by: Mapped[int] = mapped_column("ca_done_by", ForeignKey('cns_user_def.cu_user_id'), nullable=False)
    lead_id: Mapped[int] = mapped_column("ca_lead_id", ForeignKey("cns_lead_def.cl_lead_id"), nullable=True)
    activity_code: Mapped[str] = mapped_column("ca_activity_code", nullable=False)
    activity_desc: Mapped[str] = mapped_column("ca_details", nullable=True)
    affected_user: Mapped[int] = mapped_column("ca_affected_user", ForeignKey('cns_user_def.cu_user_id'), nullable=True)
    event_date: Mapped[datetime] = mapped_column("ca_activity_date", default=datetime.now())
    stage_id: Mapped[int] = mapped_column("ca_stage_id", ForeignKey("cns_lead_stage_def.ls_stage_id"), nullable=True)
    media_code: Mapped[str] = mapped_column("ca_media_code", ForeignKey("cns_media_def.cm_media_code"), nullable=True)