-- ============================================
-- ATS Portal - Complete Schema Setup (Simplified)
-- ============================================
SET QUOTED_IDENTIFIER ON;

-- 1. Master Dropdown Category
CREATE TABLE master_dropdown_category (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    value_text NVARCHAR(255) NOT NULL,
    is_active BIT DEFAULT 1
);

-- 2. Master Dropdown
CREATE TABLE master_dropdown (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    dropdown_category_id BIGINT NOT NULL REFERENCES master_dropdown_category(id),
    value_text NVARCHAR(255) NOT NULL,
    is_active BIT DEFAULT 1,
    sort_order INT DEFAULT 0
);

-- 3. User Roles
CREATE TABLE user_roles (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    role_name NVARCHAR(255) NOT NULL,
    description NVARCHAR(500) NULL,
    is_active BIT DEFAULT 1
);

-- 4. Menu Master
CREATE TABLE menu_master (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    menu_name NVARCHAR(255) NOT NULL,
    is_active BIT DEFAULT 1
);

-- 5. User Role Permissions
CREATE TABLE user_role_permissions (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    role_id BIGINT NOT NULL REFERENCES user_roles(id),
    menu_id BIGINT NOT NULL REFERENCES menu_master(id),
    is_editable BIT NOT NULL,
    is_view BIT NOT NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 6. Users
CREATE TABLE users (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    employee_code NVARCHAR(100) NOT NULL,
    username NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(255) NOT NULL,
    user_role_id BIGINT NOT NULL REFERENCES user_roles(id),
    is_active BIT DEFAULT 1 NOT NULL,
    parent_id BIGINT NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    updated_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 7. Candidate (Resume)
CREATE TABLE Candidate (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(255) NULL,
    email NVARCHAR(255) NULL,
    phone NVARCHAR(100) NULL,
    alternate_number NVARCHAR(100) NULL,
    website NVARCHAR(MAX) NULL,
    date_of_birth NVARCHAR(50) NULL,
    address NVARCHAR(MAX) NULL,
    summary NVARCHAR(MAX) NULL,
    education NVARCHAR(MAX) NULL,
    work_experience NVARCHAR(MAX) NULL,
    skills NVARCHAR(MAX) NULL,
    certifications NVARCHAR(MAX) NULL,
    projects NVARCHAR(MAX) NULL,
    file_name NVARCHAR(255) NULL,
    total_experience FLOAT NULL,
    total_experience_pretty NVARCHAR(100) NULL,
    experience_per_company NVARCHAR(MAX) NULL,
    experience_per_company_pretty NVARCHAR(MAX) NULL,
    current_company NVARCHAR(255) NULL,
    designation NVARCHAR(255) NULL,
    last_working_day DATETIME2 NULL,
    notice_period INT NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    updated_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    active BIT DEFAULT 1 NOT NULL,
    is_complete BIT DEFAULT 0 NOT NULL,
    created_by BIGINT NOT NULL REFERENCES users(id)
);

CREATE UNIQUE INDEX ux_candidate_email ON Candidate(email) WHERE email IS NOT NULL;

-- 8. Attachments
CREATE TABLE Attachments (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    candidate_id BIGINT NOT NULL UNIQUE REFERENCES Candidate(id) ON DELETE CASCADE,
    file_name NVARCHAR(255) NULL,
    file_data VARBINARY(MAX) NULL,
    file_type NVARCHAR(10) NULL,
    status NVARCHAR(50) DEFAULT 'active' NOT NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    updated_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 9. Candidate Raw Data
CREATE TABLE Candidate_Raw_Data (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    candidate_id BIGINT NOT NULL UNIQUE REFERENCES Candidate(id) ON DELETE CASCADE,
    raw_text NVARCHAR(MAX) NULL,
    parsed_json NVARCHAR(MAX) NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    updated_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 10. Resume Audit Log
CREATE TABLE Resume_Audit_Log (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    candidate_id BIGINT NULL REFERENCES Candidate(id) ON DELETE CASCADE,
    file_name NVARCHAR(255) NOT NULL,
    resume_status BIT DEFAULT 0 NOT NULL,
    free_text NVARCHAR(MAX) NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 11. Login Audit
CREATE TABLE Login_Audit (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(255) NOT NULL,
    employee_id NVARCHAR(100) NULL,
    token NVARCHAR(MAX) NOT NULL,
    created DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 12. Jobs (simplified from MRF)
CREATE TABLE jobs (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(255) NOT NULL,
    number_of_positions INT NOT NULL,
    mandatory_skills NVARCHAR(MAX) NULL,
    desired_skills NVARCHAR(MAX) NULL,
    qualification NVARCHAR(MAX) NULL,
    location NVARCHAR(255) NULL,
    experience_level NVARCHAR(255) NULL,
    job_description NVARCHAR(MAX) NULL,
    status_id BIGINT NULL REFERENCES master_dropdown(id),
    department NVARCHAR(255) NULL,
    positions_filled INT DEFAULT 0,
    created DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    updated DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    created_by BIGINT NOT NULL REFERENCES users(id),
    is_active BIT DEFAULT 1,
    expires_at DATETIME2 NULL
);

-- 13. Job Candidates
CREATE TABLE job_candidates (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES jobs(id),
    candidate_id BIGINT NOT NULL REFERENCES Candidate(id),
    current_stage_id BIGINT NULL REFERENCES master_dropdown(id),
    current_result_id BIGINT NULL REFERENCES master_dropdown(id),
    created DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    updated DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    created_by BIGINT NOT NULL,
    is_active BIT DEFAULT 1 NOT NULL,
    status NVARCHAR(50) DEFAULT 'Applied' NOT NULL
);

-- 14. Interviews
CREATE TABLE Interviews (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES jobs(id),
    job_candidate_id BIGINT NOT NULL REFERENCES job_candidates(id),
    candidate_id BIGINT NOT NULL REFERENCES Candidate(id) ON DELETE CASCADE,
    scheduled_interview_date DATE NOT NULL,
    scheduled_start_time TIME NOT NULL,
    scheduled_end_time TIME NULL,
    duration_id BIGINT NOT NULL,
    stage_id BIGINT NOT NULL,
    interviewer_id NVARCHAR(255) NOT NULL,
    is_interviewer_external BIT NOT NULL,
    interviewer_name NVARCHAR(255) NULL,
    interviewer_email_id NVARCHAR(255) NULL,
    interview_mode_id BIGINT NULL REFERENCES master_dropdown(id),
    location NVARCHAR(255) NULL,
    video_call_link NVARCHAR(500) NULL,
    additional_notes NVARCHAR(MAX) NULL,
    comments NVARCHAR(MAX) NULL,
    upload_feedback_template VARBINARY(MAX) NULL,
    feedback_filename NVARCHAR(255) NULL,
    rating_id BIGINT NULL REFERENCES master_dropdown(id),
    result_id BIGINT NULL REFERENCES master_dropdown(id),
    rejection_id BIGINT NULL REFERENCES master_dropdown(id),
    active BIT DEFAULT 1,
    status NVARCHAR(50) NOT NULL,
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    feedback_at DATETIME2 NULL,
    updated_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 15. Template Master
CREATE TABLE template_master (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    template_name NVARCHAR(255) NOT NULL,
    file_type NVARCHAR(50) NULL,
    binary_file VARBINARY(MAX) NULL,
    is_active BIT DEFAULT 1 NOT NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 16. Candidate Notes
CREATE TABLE candidate_notes (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    candidate_id BIGINT NOT NULL REFERENCES Candidate(id) ON DELETE CASCADE,
    note NVARCHAR(MAX) NOT NULL,
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 17. Stage History
CREATE TABLE stage_history (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    job_candidate_id BIGINT NOT NULL REFERENCES job_candidates(id) ON DELETE CASCADE,
    from_stage_id BIGINT NULL,
    to_stage_id BIGINT NULL,
    from_result_id BIGINT NULL,
    to_result_id BIGINT NULL,
    changed_by BIGINT NOT NULL REFERENCES users(id),
    changed_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 18. Email Templates
CREATE TABLE email_templates (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    subject NVARCHAR(500) NOT NULL,
    body_html NVARCHAR(MAX) NOT NULL,
    description NVARCHAR(500) NULL,
    is_active BIT DEFAULT 1 NOT NULL,
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    updated_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- 19. Offers
CREATE TABLE offers (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES jobs(id),
    candidate_id BIGINT NOT NULL REFERENCES Candidate(id),
    job_candidate_id BIGINT NOT NULL REFERENCES job_candidates(id),
    offered_salary NVARCHAR(100) NULL,
    joining_date DATETIME2 NULL,
    offer_notes NVARCHAR(MAX) NULL,
    status NVARCHAR(50) DEFAULT 'Pending' NOT NULL,
    rejection_reason NVARCHAR(MAX) NULL,
    created_by BIGINT NOT NULL REFERENCES users(id),
    created_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    updated_at DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);

-- ============================================
-- SEED DATA
-- ============================================

-- Default role
INSERT INTO user_roles (role_name, description, is_active) VALUES ('Admin', 'Administrator', 1);

-- Default admin user
INSERT INTO users (employee_code, username, email, full_name, user_role_id, is_active)
VALUES ('EMP001', 'admin', 'admin@local.com', 'Admin User', 1, 1);

-- Default menu items
INSERT INTO menu_master (menu_name, is_active) VALUES ('Dashboard', 1);
INSERT INTO menu_master (menu_name, is_active) VALUES ('Resumes', 1);
INSERT INTO menu_master (menu_name, is_active) VALUES ('Jobs', 1);
INSERT INTO menu_master (menu_name, is_active) VALUES ('Interviews', 1);
INSERT INTO menu_master (menu_name, is_active) VALUES ('Users', 1);

-- Admin permissions for all menus
INSERT INTO user_role_permissions (role_id, menu_id, is_editable, is_view) VALUES (1, 1, 1, 1);
INSERT INTO user_role_permissions (role_id, menu_id, is_editable, is_view) VALUES (1, 2, 1, 1);
INSERT INTO user_role_permissions (role_id, menu_id, is_editable, is_view) VALUES (1, 3, 1, 1);
INSERT INTO user_role_permissions (role_id, menu_id, is_editable, is_view) VALUES (1, 4, 1, 1);
INSERT INTO user_role_permissions (role_id, menu_id, is_editable, is_view) VALUES (1, 5, 1, 1);

-- Dropdown categories
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Interview Stage', 1);
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Interview Result', 1);
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Job Status', 1);
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Interview Mode', 1);
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Rating', 1);
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Rejection Reason', 1);
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Duration', 1);

-- Interview Stages (category 1)
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (1, 'Screening', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (1, 'Technical Round 1', 2);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (1, 'Technical Round 2', 3);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (1, 'HR Round', 4);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (1, 'Final Round', 5);

-- Interview Results (category 2)
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (2, 'Selected', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (2, 'Rejected', 2);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (2, 'On Hold', 3);

-- Job Status (category 3)
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (3, 'Open', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (3, 'In Progress', 2);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (3, 'Closed', 3);

-- Interview Mode (category 4)
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (4, 'Video Call', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (4, 'In-Person', 2);

-- Rating (category 5)
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (5, '1 - Poor', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (5, '2 - Below Average', 2);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (5, '3 - Average', 3);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (5, '4 - Good', 4);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (5, '5 - Excellent', 5);

-- Rejection Reason (category 6)
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (6, 'Not a fit', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (6, 'Salary mismatch', 2);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (6, 'Candidate declined', 3);

-- Duration (category 7)
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (7, '30 Minutes', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (7, '45 Minutes', 2);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (7, '60 Minutes', 3);

-- Candidate Status (category 8)
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Candidate Status', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (8, 'Applied', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (8, 'Screening', 2);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (8, 'Interview', 3);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (8, 'Offered', 4);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (8, 'Hired', 5);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (8, 'Rejected', 6);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (8, 'Withdrawn', 7);

-- Offer Status (category 9)
INSERT INTO master_dropdown_category (value_text, is_active) VALUES ('Offer Status', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (9, 'Pending', 1);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (9, 'Accepted', 2);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (9, 'Rejected', 3);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (9, 'Negotiating', 4);
INSERT INTO master_dropdown (dropdown_category_id, value_text, sort_order) VALUES (9, 'Withdrawn', 5);

-- Default email templates
INSERT INTO email_templates (name, subject, body_html, description) VALUES (
    'interview_candidate',
    'Interview {{action}} - {{candidate_name}}: {{date}}',
    '<h2>Interview {{action}}</h2><p>Dear {{candidate_name}},</p><p>Your interview has been {{action}} with the following details:</p><ul><li><strong>Date:</strong> {{date}}</li><li><strong>Time:</strong> {{start_time}} - {{end_time}}</li><li><strong>Interviewer:</strong> {{interviewer_name}}</li>{{mode_details}}</ul><p>Good luck!</p>',
    'Sent to candidate when interview is scheduled/rescheduled'
);
INSERT INTO email_templates (name, subject, body_html, description) VALUES (
    'interview_interviewer',
    'Interview {{action}} - {{candidate_name}}: {{date}}',
    '<h2>Interview {{action}}</h2><p>Dear {{interviewer_name}},</p><p>An interview has been {{action}} with the following details:</p><ul><li><strong>Candidate:</strong> {{candidate_name}}</li><li><strong>Date:</strong> {{date}}</li><li><strong>Time:</strong> {{start_time}} - {{end_time}}</li>{{mode_details}}<li><strong>Feedback Link:</strong> <a href="{{feedback_url}}">{{feedback_url}}</a></li></ul>',
    'Sent to interviewer when interview is scheduled/rescheduled'
);

-- Offers menu
INSERT INTO menu_master (menu_name, is_active) VALUES ('Offers', 1);
INSERT INTO user_role_permissions (role_id, menu_id, is_editable, is_view) VALUES (1, 6, 1, 1);

PRINT 'All tables and seed data created successfully!';
