from datetime import datetime, UTC

from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, Boolean, Text, DateTime, DECIMAL
from sqlalchemy.orm import Mapped

from app.src.core.models.db_models import Base


class Job(Base):
    __tablename__ = 'job'
    job_id: Mapped[int] = Column(Integer, primary_key=True)
    job_status: Mapped[str] = Column(
        Enum('Draft', 'Active', 'Closed WON', 'Closed', 'On Hold', 'Cancelled', 'Target Date', 'Expired'),
        nullable=False)
    job_title: Mapped[str] = Column(String(255), nullable=False)
    customer_type: Mapped[str] = Column(Enum('Internal', 'Vendor', 'Prime Vendor', 'Direct Client'), nullable=False)
    account_id: Mapped[int] = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    show_client_vendor_info: Mapped[bool] = Column(Boolean)
    publish: Mapped[bool] = Column(Boolean, default=True)
    city: Mapped[str] = Column(String(255))
    country: Mapped[str] = Column(String(255))
    state: Mapped[str] = Column(String(255))
    zip_code: Mapped[str] = Column(String(10))
    no_of_positions: Mapped[int] = Column(Integer)
    target_date: Mapped[datetime] = Column(Date)
    remote_status: Mapped[str] = Column(Enum('On Site', 'Remote', 'Hybrid'), nullable=False)
    qualifications: Mapped[str] = Column(
        Enum('High School', 'Military Service', 'Associate', 'Pre Bachelors', 'Bachelors', 'Post Bachelors', 'Masters',
             'Doctorate'), nullable=False)
    industry_id: Mapped[int] = Column(Integer, ForeignKey('industry.industry_id'), nullable=False)
    client_job_id: Mapped[str] = Column(String(255))
    salary: Mapped[DECIMAL] = Column(DECIMAL(10, 2))
    pay_billing_details: Mapped[str] = Column(Text)
    job_description: Mapped[str] = Column(Text)
    job_domain_id: Mapped[int] = Column(Integer, ForeignKey('job_domains.job_domain_id'))
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now(UTC))
    modified_at: Mapped[datetime] = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    deleted_at: Mapped[datetime] = Column(DateTime)


class JobRecruiter(Base):
    __tablename__ = 'job_recruiters'
    job_id: Mapped[int] = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'),
                                 primary_key=True)
    recruiter_id: Mapped[int] = Column(Integer,
                                       ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE', onupdate='CASCADE'),
                                       primary_key=True)


class JobAdditionalRecruiter(Base):
    __tablename__ = 'job_additional_recruiters'
    job_id: Mapped[int] = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'),
                                 primary_key=True)
    additional_recruiter_id: Mapped[int] = Column(Integer, ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE',
                                                                      onupdate='CASCADE'), primary_key=True)


class JobAccountManager(Base):
    __tablename__ = 'job_account_managers'
    job_id: Mapped[int] = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'),
                                 primary_key=True)
    account_manager_id: Mapped[int] = Column(Integer, ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE',
                                                                 onupdate='CASCADE'), primary_key=True)


class JobSourcer(Base):
    __tablename__ = 'job_sourcers'
    job_id: Mapped[int] = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'),
                                 primary_key=True)
    sourcer_id: Mapped[int] = Column(Integer,
                                     ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE', onupdate='CASCADE'),
                                     primary_key=True)


class JobRecruitmentManager(Base):
    __tablename__ = 'job_recruitment_managers'
    job_id: Mapped[int] = Column(Integer, ForeignKey('job.job_id', ondelete='CASCADE', onupdate='CASCADE'),
                                 primary_key=True)
    recruitment_manager_id: Mapped[int] = Column(Integer, ForeignKey('cns_user_def.cu_user_id', ondelete='CASCADE',
                                                                     onupdate='CASCADE'), primary_key=True)
