from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.types import DECIMAL

from app.src.core.models.db_models import Base


class Job(Base):
    __tablename__ = 'job'
    job_id = Column(Integer, primary_key=True)
    job_status = Column(
        Enum('Draft', 'Active', 'Closed WON', 'Closed', 'On Hold', 'Cancelled', 'Target Date', 'Expired'),
        nullable=False)
    job_title = Column(String(255), nullable=False)
    customer_type = Column(Enum('Internal', 'Vendor', 'Prime Vendor', 'Direct Client'), nullable=False)
    account_id = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    show_client_vendor_info = Column(Boolean)
    publish = Column(Boolean, default=True)
    city = Column(String(255))
    country = Column(String(255))
    state = Column(String(255))
    zip_code = Column(String(10))
    no_of_positions = Column(Integer)
    target_date = Column(Date)
    remote_status = Column(Enum('On Site', 'Remote', 'Hybrid'), nullable=False)
    qualifications = Column(
        Enum('High School', 'Military Service', 'Associate', 'Pre Bachelors', 'Bachelors', 'Post Bachelors', 'Masters',
             'Doctorate'), nullable=False)
    industry_id = Column(Integer, ForeignKey('industry.industry_id'), nullable=False)
    client_job_id = Column(String(255))
    salary = Column(DECIMAL(10, 2))
    pay_billing_details = Column(Text)
    job_description = Column(Text)
    job_domain_id = Column(Integer, ForeignKey('job_domains.job_domain_id'))
    created_at = Column(DateTime, default=datetime.now(UTC))
    modified_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_at = Column(DateTime)


class JobRecruiter(Base):
    __tablename__ = 'job_recruiters'
    job_id = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    recruiter_id = Column(Integer, ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE', onupdate='CASCADE'),
                          primary_key=True)


class JobAdditionalRecruiter(Base):
    __tablename__ = 'job_additional_recruiters'
    job_id = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    additional_recruiter_id = Column(Integer,
                                     ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE', onupdate='CASCADE'),
                                     primary_key=True)


class JobAccountManager(Base):
    __tablename__ = 'job_account_managers'
    job_id = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    account_manager_id = Column(Integer, ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE', onupdate='CASCADE'),
                                primary_key=True)


class JobSourcer(Base):
    __tablename__ = 'job_sourcers'
    job_id = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    sourcer_id = Column(Integer, ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True)


class JobRecruitmentManager(Base):
    __tablename__ = 'job_recruitment_managers'
    job_id = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    recruitment_manager_id = Column(Integer,
                                    ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE', onupdate='CASCADE'),
                                    primary_key=True)
