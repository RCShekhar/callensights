from sqlalchemy import Column, Integer, String, ForeignKey

from app.src.core.models.db_models import Base


class Industry(Base):
    __tablename__ = 'industry'
    industry_id = Column(Integer, primary_key=True)
    industry_name = Column(String(255), nullable=False)


class JobDomains(Base):
    __tablename__ = 'job_domains'
    job_domain_id = Column(Integer, primary_key=True)
    domain_name = Column(String(255), nullable=False)


class Skills(Base):
    __tablename__ = 'skills'
    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    skill_name = Column(String(255), nullable=False)


class JobPrimarySkill(Base):
    __tablename__ = 'job_primary_skills'
    job_id = Column(Integer, ForeignKey('job.job_id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('skills.skill_id'), primary_key=True)


class JobSecondarySkill(Base):
    __tablename__ = 'job_secondary_skills'
    job_id = Column(Integer, ForeignKey('job.job_id'), primary_key=True)
    skill_id = Column(Integer, ForeignKey('skills.skill_id'), primary_key=True)


class Source(Base):
    __tablename__ = 'source'
    source_id = Column(Integer, autoincrement=True, primary_key=True)
    source_name = Column(String(255), nullable=False)


class EmploymentType(Base):
    __tablename__ = 'employment_type'
    employment_type_id = Column(Integer, autoincrement=True, primary_key=True)
    type_name = Column(String(255), nullable=False)


class LanguagesKnown(Base):
    __tablename__ = 'languages_known'
    language_id = Column(Integer, autoincrement=True, primary_key=True)
    language_name = Column(String(255), nullable=False)


class WorkAuthorization(Base):
    __tablename__ = 'work_authorization'
    authorization_id = Column(Integer, autoincrement=True, primary_key=True)
    authorization_name = Column(String(255), nullable=False)


class EngagementType(Base):
    __tablename__ = 'engagement_types'
    engagement_type_id = Column(Integer, autoincrement=True, primary_key=True)
    engagement_type_name = Column(String(255), nullable=False)


class PayType(Base):
    __tablename__ = 'pay_types'
    pay_type_id = Column(Integer, autoincrement=True, primary_key=True)
    pay_type_name = Column(String(255), nullable=False)
