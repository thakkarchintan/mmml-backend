CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    company VARCHAR(255),
    job_title VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE event_registrations (
    registration_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    years_of_experience VARCHAR(50),
    topics_of_interest TEXT,
    dietary_restrictions TEXT,
    referral_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE waitlist_registrations (
    waitlist_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    reason_to_attend TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE contact_messages (
    message_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company_organization VARCHAR(255),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE speaker_applications (
    application_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    job_title VARCHAR(255) NOT NULL,
    linkedin_profile VARCHAR(255),
    area_of_expertise VARCHAR(100) NOT NULL,
    proposed_topic_title VARCHAR(255) NOT NULL,
    topic_description TEXT NOT NULL,
    speaking_experience VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sponsorship_inquiries (
    inquiry_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    company_website VARCHAR(255),
    interested_sponsorship_level VARCHAR(100),
    marketing_objectives TEXT NOT NULL,
    budget_range VARCHAR(50),
    timeline VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE partnership_proposals (
    proposal_id SERIAL PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    organization_website VARCHAR(255),
    partnership_type VARCHAR(100) NOT NULL,
    partnership_proposal TEXT NOT NULL,
    audience_community TEXT,
    resources_contributed TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE volunteer_applications (
    application_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    profession VARCHAR(255) NOT NULL,
    company_organization VARCHAR(255),
    volunteer_experience VARCHAR(50),
    availability VARCHAR(50) NOT NULL,
    relevant_skills_experience TEXT NOT NULL,
    areas_of_interest TEXT NOT NULL,
    motivation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);