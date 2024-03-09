-- CREATE SCHEMA callensights;

CREATE  TABLE callensights.cns_application_config (
	ac_config_id         INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	ac_config_key        VARCHAR(50)    NOT NULL   ,
	cns_config_value     VARCHAR(100)       ,
	ac_config_desc       VARCHAR(200)       ,
	ac_created_dt        DATETIME  DEFAULT (now())     ,
	ac_update_dt         DATETIME       ,
	CONSTRAINT unq_cns_application_config UNIQUE ( ac_config_key )
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE  TABLE callensights.cns_lead_stage_def (
	ls_stage_id          INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	ls_stage_code        VARCHAR(20)   CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL   ,
	ls_stage_desc        VARCHAR(512)   CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci    ,
	ls_is_active         BOOLEAN  DEFAULT ('1')     ,
	ls_created_dt        DATETIME  DEFAULT (CURRENT_TIMESTAMP)     ,
	ls_modified_dt       DATETIME  DEFAULT (CURRENT_TIMESTAMP)     ,
	CONSTRAINT unq_cns_call_types_def UNIQUE ( ls_stage_code )
 ) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE  TABLE callensights.cns_lead_types_def (
	lt_type_id           INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	lt_type_desc         VARCHAR(256)       ,
	lt_created_dt        DATETIME  DEFAULT (now())  NOT NULL   ,
	lt_type_code         VARCHAR(10)    NOT NULL   ,
	CONSTRAINT unq_cns_lead_types_def UNIQUE ( lt_type_code )
 ) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE  TABLE callensights.cns_metrics_def (
	md_metric_id         INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	md_metric_title      VARCHAR(50)       ,
	md_metric_prompt     VARCHAR(512)       ,
	md_metric_created_dt DATETIME  DEFAULT (now())     ,
	md_metric_updated_dt DATETIME   ON UPDATE CURRENT_TIMESTAMP
 ) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE  TABLE callensights.cns_user_group (
	ug_group_id          INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	ug_group_name        VARCHAR(20)    NOT NULL   ,
	ug_group_desc        VARCHAR(200)       ,
	ug_created_dt        DATETIME  DEFAULT (now())     ,
	ug_end_dt            DATETIME       ,
	CONSTRAINT `cns_user_group_UN` UNIQUE ( ug_group_name )
 ) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE  TABLE callensights.cns_group_message (
	gm_msg_id            INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	gm_group_id          INT    NOT NULL   ,
	gm_msg_order         INT       ,
	gm_message           MEDIUMTEXT       ,
	gm_msg_status        CHAR(1)  DEFAULT ('Y')  NOT NULL   ,
	gm_created_dt        DATETIME  DEFAULT (now())     ,
	gm_end_dt            DATETIME       ,
	CONSTRAINT fk_cns_group_message FOREIGN KEY ( gm_group_id ) REFERENCES callensights.cns_user_group( ug_group_id ) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX fk_cns_group_message ON callensights.cns_group_message ( gm_group_id );

CREATE  TABLE callensights.cns_lead_call_metrics (
	lcm_id               INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	lcm_lead_type_id     INT       ,
	lcm_call_type_id     INT       ,
	lcm_metrics_id       INT       ,
	lcm_created_dt       DATETIME  DEFAULT (now())     ,
	lcm_key_metric       CHAR(1)  DEFAULT ('N')     ,
	CONSTRAINT fk_cns_lead_call_metrics FOREIGN KEY ( lcm_lead_type_id ) REFERENCES callensights.cns_lead_types_def( lt_type_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT fk_cns_lead_call_metrics_call_type FOREIGN KEY ( lcm_call_type_id ) REFERENCES callensights.cns_lead_stage_def( ls_stage_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT fk_cns_lead_call_metrics_metric FOREIGN KEY ( lcm_metrics_id ) REFERENCES callensights.cns_metrics_def( md_metric_id ) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX fk_cns_lead_call_metrics ON callensights.cns_lead_call_metrics ( lcm_lead_type_id );

CREATE INDEX fk_cns_lead_call_metrics_call_type ON callensights.cns_lead_call_metrics ( lcm_call_type_id );

CREATE INDEX fk_cns_lead_call_metrics_metric ON callensights.cns_lead_call_metrics ( lcm_metrics_id );

CREATE  TABLE callensights.cns_user_def (
	cu_user_id           INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	cu_clerk_user_id     VARCHAR(100)       ,
	cu_user_name         VARCHAR(45)       ,
	cu_first_name        VARCHAR(100)    NOT NULL   ,
	cu_middle_name       VARCHAR(100)       ,
	cu_last_name         VARCHAR(100)       ,
	cu_email             VARCHAR(200)       ,
	cu_ph                VARCHAR(20)       ,
	cu_organization      VARCHAR(100)       ,
	cu_role              VARCHAR(100)       ,
	cu_image_url         VARCHAR(1024)       ,
	cu_manager_id        INT       ,
	cu_user_group_id     INT    NOT NULL   ,
	cu_created_dt        DATE  DEFAULT (curdate())     ,
	cu_updated_dt        DATE  DEFAULT (curdate())     ,
	CONSTRAINT unq_cns_clerk_user_id UNIQUE ( cu_clerk_user_id ) ,
	CONSTRAINT `cns_user_def_FK` FOREIGN KEY ( cu_manager_id ) REFERENCES callensights.cns_user_def( cu_user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT fk_cns_user_def_cns_user_group FOREIGN KEY ( cu_user_group_id ) REFERENCES callensights.cns_user_group( ug_group_id ) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX fk_cns_user_def_cns_user_group ON callensights.cns_user_def ( cu_user_group_id );

CREATE INDEX `cns_user_def_FK` ON callensights.cns_user_def ( cu_manager_id );

CREATE  TABLE callensights.cns_lead_def (
	cl_lead_id           INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	cl_lead_name         VARCHAR(100)       ,
	cl_email             VARCHAR(128)       ,
	cl_phone             VARCHAR(100)    NOT NULL   ,
	cl_country           CHAR(2)       ,
	cl_state_province    VARCHAR(50)   CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci    ,
	cl_stage_id          INT       ,
	cl_assigned_to       INT       ,
	cl_lead_desc         VARCHAR(1024)       ,
	cl_type_code         VARCHAR(10)   CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci    ,
	cl_created_dt        DATETIME  DEFAULT (now())  NOT NULL   ,
	cl_updated_dt        DATETIME   ON UPDATE CURRENT_TIMESTAMP    ,
	CONSTRAINT unq_cns_lead_def UNIQUE ( cl_phone ) ,
	CONSTRAINT `cns_lead_def_FK` FOREIGN KEY ( cl_stage_id ) REFERENCES callensights.cns_lead_stage_def( ls_stage_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT `cns_lead_def_FK_1` FOREIGN KEY ( cl_assigned_to ) REFERENCES callensights.cns_user_def( cu_user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT fk_cns_lead_def FOREIGN KEY ( cl_type_code ) REFERENCES callensights.cns_lead_types_def( lt_type_code ) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) ENGINE=InnoDB AUTO_INCREMENT=115 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX fk_cns_lead_def ON callensights.cns_lead_def ( cl_type_code );

CREATE INDEX `cns_lead_def_FK` ON callensights.cns_lead_def ( cl_stage_id );

CREATE INDEX `cns_lead_def_FK_1` ON callensights.cns_lead_def ( cl_assigned_to );

CREATE  TABLE callensights.cns_media_def (
	cm_media_id          INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	cm_media_code        VARCHAR(100)   CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci    ,
	cm_user_id           INT    NOT NULL   ,
	cm_original_name     VARCHAR(100)       ,
	cm_file_type         VARCHAR(10)       ,
	cm_store_file        VARCHAR(100)       ,
	cm_media_length      BIGINT       ,
	cm_media_size        BIGINT       ,
	cm_bucket            VARCHAR(100)       ,
	cm_event_dt          DATETIME  DEFAULT (now())     ,
	cm_is_uploaded       BOOLEAN  DEFAULT ('0')  NOT NULL   ,
	cm_rep_name          VARCHAR(100)       ,
	cm_conv_type         VARCHAR(100)       ,
	cm_demography        VARCHAR(100)       ,
	cm_lang_code         VARCHAR(10)       ,
	cm_product           VARCHAR(50)       ,
	cm_lead_id           INT       ,
	CONSTRAINT unq_cns_media_def UNIQUE ( cm_media_code ) ,
	CONSTRAINT fk_cns_media_def_cns_lead_def FOREIGN KEY ( cm_lead_id ) REFERENCES callensights.cns_lead_def( cl_lead_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT fk_cns_media_def_cns_user_def FOREIGN KEY ( cm_user_id ) REFERENCES callensights.cns_user_def( cu_user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX fk_cns_media_def_cns_user_def ON callensights.cns_media_def ( cm_user_id );

CREATE INDEX fk_cns_media_def_cns_lead_def ON callensights.cns_media_def ( cm_lead_id );

CREATE  TABLE callensights.cns_media_status (
	ms_status_id         INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	ms_media_id          INT    NOT NULL   ,
	ms_trans_status_cd   CHAR(1)  DEFAULT ('N')     ,
	ms_trans_start_dt    DATETIME       ,
	ms_trans_end_dt      DATETIME       ,
	ms_fedbk_status_cd   CHAR(1)  DEFAULT ('N')     ,
	ms_fedbk_start_dt    DATETIME       ,
	ms_fedbk_end_dt      DATETIME       ,
	ms_comments          VARCHAR(200)       ,
	ms_stage_inputs      VARCHAR(1000)       ,
	CONSTRAINT unq_cns_media_status UNIQUE ( ms_media_id ) ,
	CONSTRAINT fk_cns_media_status FOREIGN KEY ( ms_media_id ) REFERENCES callensights.cns_media_def( cm_media_id ) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE  TABLE callensights.cns_activity (
	ca_activity_id       INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	ca_lead_id           INT    NOT NULL   ,
	ca_done_by           INT       ,
	ca_activity_code     VARCHAR(20)    NOT NULL   ,
	ca_details           VARCHAR(512)       ,
	ca_affected_user     INT       ,
	ca_activity_date     DATETIME  DEFAULT (now())  NOT NULL   ,
	ca_stage_id          INT       ,
	ca_media_code        VARCHAR(100)       ,
	CONSTRAINT cns_activity_fk_0 FOREIGN KEY ( ca_done_by ) REFERENCES callensights.cns_user_def( cu_user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT cns_activity_fk_3 FOREIGN KEY ( ca_affected_user ) REFERENCES callensights.cns_user_def( cu_user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT cns_activity_fk_4 FOREIGN KEY ( ca_stage_id ) REFERENCES callensights.cns_lead_stage_def( ls_stage_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT fk_cns_activity_cns_lead_def_0 FOREIGN KEY ( ca_lead_id ) REFERENCES callensights.cns_lead_def( cl_lead_id ) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) ENGINE=InnoDB AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE INDEX fk_cns_activity_cns_lead_def ON callensights.cns_activity ( ca_lead_id );

CREATE INDEX `cns_activity_FK` ON callensights.cns_activity ( ca_done_by );

CREATE INDEX `cns_activity_FK_1` ON callensights.cns_activity ( ca_affected_user );

CREATE INDEX `cns_activity_FK_2` ON callensights.cns_activity ( ca_stage_id );

CREATE  TABLE callensights.cns_colab_def (
	co_colab_id          INT    NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	co_lead_id           INT    NOT NULL   ,
	co_user_id           INT    NOT NULL   ,
	co_created_dt        DATE  DEFAULT (curdate())     ,
	co_end_dt            DATE       ,
	CONSTRAINT fk_cns_colab_def_cns_lead_def FOREIGN KEY ( co_lead_id ) REFERENCES callensights.cns_lead_def( cl_lead_id ) ON DELETE NO ACTION ON UPDATE NO ACTION,
	CONSTRAINT fk_cns_colab_def_cns_user_def_2 FOREIGN KEY ( co_user_id ) REFERENCES callensights.cns_user_def( cu_user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION
 ) engine=InnoDB;

CREATE INDEX fk_cns_colab_def_cns_lead_def ON callensights.cns_colab_def ( co_lead_id );

CREATE VIEW callensights.metrics_view AS select `cmd2`.`cm_media_code` AS `media_code`,`cltd`.`lt_type_desc` AS `lead_type_desc`,`clsd`.`ls_stage_desc` AS `stage_desc`,`cld`.`cl_lead_name` AS `lead_name`,`cmd`.`md_metric_prompt` AS `metric_prompt`,`clcm`.`lcm_key_metric` AS `key_metric_flag` from (((((`callensights`.`cns_lead_call_metrics` `clcm` join `callensights`.`cns_metrics_def` `cmd` on((`cmd`.`md_metric_id` = `clcm`.`lcm_metrics_id`))) join `callensights`.`cns_lead_types_def` `cltd` on((`clcm`.`lcm_lead_type_id` = `cltd`.`lt_type_id`))) join `callensights`.`cns_lead_stage_def` `clsd` on((`clsd`.`ls_stage_id` = `clcm`.`lcm_call_type_id`))) join `callensights`.`cns_lead_def` `cld` on((`cld`.`cl_stage_id` = `clsd`.`ls_stage_id`))) join `callensights`.`cns_media_def` `cmd2` on((`cmd2`.`cm_lead_id` = `cld`.`cl_lead_id`)));


CREATE TRIGGER callensights.trg_media_status AFTER INSERT ON cns_media_def FOR EACH ROW BEGIN
	INSERT INTO cns_media_status (ms_media_id)
	VALUES(NEW.cm_media_id);
END; //


CREATE TRIGGER callensights.trg_status_update BEFORE UPDATE ON cns_media_status FOR EACH ROW BEGIN
    IF NEW.ms_trans_status_cd = 'R' THEN
        SET NEW.ms_trans_start_dt = CURRENT_TIMESTAMP();
    ELSEIF NEW.ms_trans_status_cd IN ('C', 'S', 'E') THEN
        SET NEW.ms_trans_end_dt = CURRENT_TIMESTAMP();
    END IF;
    IF NEW.ms_fedbk_status_cd = 'R' THEN
        SET NEW.ms_fedbk_start_dt = CURRENT_TIMESTAMP();
    ELSEIF NEW.ms_fedbk_status_cd IN ('C', 'S', 'E') THEN
        SET NEW.ms_fedbk_end_dt = CURRENT_TIMESTAMP();
    END IF;
END; //

ALTER TABLE callensights.cns_application_config COMMENT 'Aplication configurations';

ALTER TABLE callensights.cns_application_config MODIFY ac_config_id INT  NOT NULL  AUTO_INCREMENT COMMENT 'Unique serial number';

ALTER TABLE callensights.cns_application_config MODIFY ac_config_key VARCHAR(50)  NOT NULL   COMMENT 'configuration key';

ALTER TABLE callensights.cns_application_config MODIFY cns_config_value VARCHAR(100)     COMMENT 'value assiciated with key. all the values are stored as varchar, in case of dates format YYYY-MM-DD';

ALTER TABLE callensights.cns_application_config MODIFY ac_config_desc VARCHAR(200)     COMMENT 'description of the configuration';

ALTER TABLE callensights.cns_application_config MODIFY ac_created_dt DATETIME   DEFAULT (now())  COMMENT 'timestamp when created';

ALTER TABLE callensights.cns_application_config MODIFY ac_update_dt DATETIME     COMMENT 'timestamp when updated';

ALTER TABLE callensights.cns_lead_types_def MODIFY lt_type_id INT  NOT NULL  AUTO_INCREMENT COMMENT 'Lead type id';

ALTER TABLE callensights.cns_user_group COMMENT 'user groups';

ALTER TABLE callensights.cns_user_group MODIFY ug_group_id INT  NOT NULL  AUTO_INCREMENT COMMENT 'Unique sequence number to identify a user group';

ALTER TABLE callensights.cns_user_group MODIFY ug_group_name VARCHAR(20)  NOT NULL   COMMENT 'unique name of the user group';

ALTER TABLE callensights.cns_user_group MODIFY ug_group_desc VARCHAR(200)     COMMENT 'description of the user group';

ALTER TABLE callensights.cns_user_group MODIFY ug_created_dt DATETIME   DEFAULT (now())  COMMENT 'the date when the user group created';

ALTER TABLE callensights.cns_user_group MODIFY ug_end_dt DATETIME     COMMENT 'End date when user doesnt need the goup';

ALTER TABLE callensights.cns_group_message COMMENT 'message of the groups';

ALTER TABLE callensights.cns_group_message MODIFY gm_group_id INT  NOT NULL   COMMENT 'group id to which the message is related to';

ALTER TABLE callensights.cns_group_message MODIFY gm_msg_order INT     COMMENT 'the message order or priority order';

ALTER TABLE callensights.cns_group_message MODIFY gm_message MEDIUMTEXT     COMMENT 'the message';

ALTER TABLE callensights.cns_group_message MODIFY gm_msg_status CHAR(1)  NOT NULL DEFAULT ('Y')  COMMENT 'Y - Active, N-Inactive';

ALTER TABLE callensights.cns_group_message MODIFY gm_created_dt DATETIME   DEFAULT (now())  COMMENT 'timestamp when created';

ALTER TABLE callensights.cns_user_def COMMENT 'Callensights user definition table';

ALTER TABLE callensights.cns_user_def MODIFY cu_user_id INT  NOT NULL  AUTO_INCREMENT COMMENT 'Unique user sequence number';

ALTER TABLE callensights.cns_user_def MODIFY cu_clerk_user_id VARCHAR(100)     COMMENT 'the userid generated by clerk';

ALTER TABLE callensights.cns_user_def MODIFY cu_user_name VARCHAR(45)     COMMENT 'unique user name, typically used as a login user';

ALTER TABLE callensights.cns_user_def MODIFY cu_first_name VARCHAR(100)  NOT NULL   COMMENT 'First name of the user';

ALTER TABLE callensights.cns_user_def MODIFY cu_middle_name VARCHAR(100)     COMMENT 'Middle name of the user';

ALTER TABLE callensights.cns_user_def MODIFY cu_last_name VARCHAR(100)     COMMENT 'Last name of the user';

ALTER TABLE callensights.cns_user_def MODIFY cu_email VARCHAR(200)     COMMENT 'email of the user';

ALTER TABLE callensights.cns_user_def MODIFY cu_organization VARCHAR(100)     COMMENT 'Organization of the user';

ALTER TABLE callensights.cns_user_def MODIFY cu_role VARCHAR(100)     COMMENT 'Role or designation of the user';

ALTER TABLE callensights.cns_user_def MODIFY cu_user_group_id INT  NOT NULL   COMMENT 'user group to which the user belongs to. refers to group id from usergroup table';

ALTER TABLE callensights.cns_user_def MODIFY cu_created_dt DATE   DEFAULT (curdate())  COMMENT 'the date when the user first signed up';

ALTER TABLE callensights.cns_user_def MODIFY cu_updated_dt DATE   DEFAULT (curdate())  COMMENT 'the date when changes happend to user profile';

ALTER TABLE callensights.cns_lead_def COMMENT 'Table contains lead definition';

ALTER TABLE callensights.cns_lead_def MODIFY cl_lead_id INT  NOT NULL  AUTO_INCREMENT COMMENT 'Unique Lead identification number';

ALTER TABLE callensights.cns_lead_def MODIFY cl_lead_name VARCHAR(100)     COMMENT 'Lead full name';

ALTER TABLE callensights.cns_lead_def MODIFY cl_email VARCHAR(128)     COMMENT 'email of leade';

ALTER TABLE callensights.cns_lead_def MODIFY cl_phone VARCHAR(100)  NOT NULL   COMMENT 'phone number of lead';

ALTER TABLE callensights.cns_lead_def MODIFY cl_country CHAR(2)     COMMENT 'country of the lead';

ALTER TABLE callensights.cns_lead_def MODIFY cl_state_province VARCHAR(50)     COMMENT 'state or province of the lead';

ALTER TABLE callensights.cns_media_def COMMENT 'uploaded media details table';

ALTER TABLE callensights.cns_media_def MODIFY cm_media_id INT  NOT NULL  AUTO_INCREMENT COMMENT 'unique media identification sequence number';

ALTER TABLE callensights.cns_media_def MODIFY cm_user_id INT  NOT NULL   COMMENT 'Unique ID of the user who uploaded the media file';

ALTER TABLE callensights.cns_media_def MODIFY cm_original_name VARCHAR(100)     COMMENT 'the original name of the media file';

ALTER TABLE callensights.cns_media_def MODIFY cm_file_type VARCHAR(10)     COMMENT 'Type or extension of the media file';

ALTER TABLE callensights.cns_media_def MODIFY cm_store_file VARCHAR(100)     COMMENT 'the name of the  media file stored as in storage bucket';

ALTER TABLE callensights.cns_media_def MODIFY cm_media_length BIGINT     COMMENT 'length of the media in secs';

ALTER TABLE callensights.cns_media_def MODIFY cm_media_size BIGINT     COMMENT 'size of the media in bytes';

ALTER TABLE callensights.cns_media_def MODIFY cm_bucket VARCHAR(100)     COMMENT 'Name of the storage bucket where all the media files stored';

ALTER TABLE callensights.cns_media_def MODIFY cm_event_dt DATETIME   DEFAULT (now())  COMMENT 'The date and time when the media file was registered';

ALTER TABLE callensights.cns_media_def MODIFY cm_rep_name VARCHAR(100)     COMMENT 'representative name. Typically the user who uploaded the media file';

ALTER TABLE callensights.cns_media_def MODIFY cm_conv_type VARCHAR(100)     COMMENT 'conversation type';

ALTER TABLE callensights.cns_media_def MODIFY cm_demography VARCHAR(100)     COMMENT 'Demography of the lead';

ALTER TABLE callensights.cns_media_def MODIFY cm_lang_code VARCHAR(10)     COMMENT 'Language code of the conversation.';

ALTER TABLE callensights.cns_media_def MODIFY cm_product VARCHAR(50)     COMMENT 'name of the product.';

ALTER TABLE callensights.cns_media_def MODIFY cm_lead_id INT     COMMENT 'lead id refering to leads def';

ALTER TABLE callensights.cns_media_status COMMENT 'Process status of media';

ALTER TABLE callensights.cns_media_status MODIFY ms_media_id INT  NOT NULL   COMMENT 'Media id refer to media def table';

ALTER TABLE callensights.cns_media_status MODIFY ms_trans_status_cd CHAR(1)   DEFAULT ('N')  COMMENT 'Status code of transcription generation N-New, R-Running, S-Success, E-Error';

ALTER TABLE callensights.cns_media_status MODIFY ms_trans_start_dt DATETIME     COMMENT 'date time when transcription process started';

ALTER TABLE callensights.cns_media_status MODIFY ms_trans_end_dt DATETIME     COMMENT 'Date time when transcription process ended';

ALTER TABLE callensights.cns_media_status MODIFY ms_fedbk_status_cd CHAR(1)   DEFAULT ('N')  COMMENT 'Status code of feedback generation N-New, R-Running, S-Success, E-Error';

ALTER TABLE callensights.cns_media_status MODIFY ms_fedbk_start_dt DATETIME     COMMENT 'date time when feedback process started';

ALTER TABLE callensights.cns_media_status MODIFY ms_comments VARCHAR(200)     COMMENT 'comments on the process completion';

ALTER TABLE callensights.cns_media_status MODIFY ms_stage_inputs VARCHAR(1000)     COMMENT 'input or SQS message string';

CREATE  TABLE cns_ats.cns_accounts (
	account_id           INT   NOT NULL AUTO_INCREMENT  PRIMARY KEY,
	account_name         VARCHAR(100)    NOT NULL   ,
	display_name         VARCHAR(100)       ,
	account_status       BOOLEAN  DEFAULT (1)  NOT NULL   ,
	account_owner        INT  NOT NULL   ,
	account_type         INT  UNSIGNED   ,
	website              VARCHAR(256)    NOT NULL   ,
	industry             VARCHAR(32)       ,
	contract_start_dt    DATE  DEFAULT (CURRENT_DATE)  NOT NULL   ,
	contract_end_dt      DATE       ,
	job_submission_workflow INT UNSIGNED      ,
	created_by           INT    NOT NULL   ,
	created_dt           DATETIME  DEFAULT (CURRENT_TIMESTAMP)  NOT NULL   ,
	modified_by          INT       ,
	modified_dt          DATETIME   ON UPDATE CURRENT_TIMESTAMP
 ) engine=InnoDB;

ALTER TABLE cns_ats.cns_accounts ADD CONSTRAINT fk_cns_accounts_type FOREIGN KEY ( account_type ) REFERENCES cns_ats.cns_account_type( type_id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE cns_ats.cns_accounts ADD CONSTRAINT fk_cns_accounts_workflow FOREIGN KEY ( job_submission_workflow ) REFERENCES cns_ats.cns_job_submission_workflow( workflow_id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE cns_ats.cns_accounts ADD CONSTRAINT fk_cns_accounts_created FOREIGN KEY ( created_by ) REFERENCES cns_ats.cns_user_def( cu_user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION;

ALTER TABLE cns_ats.cns_accounts ADD CONSTRAINT fk_cns_accounts_modified FOREIGN KEY ( modified_by ) REFERENCES cns_ats.cns_user_def( cu_user_id ) ON DELETE NO ACTION ON UPDATE NO ACTION;
