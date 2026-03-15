export interface UserProfile {
  user_id: string;
  name: string;
  email: string;
  phone?: string;
  location?: string;
}

export interface ResumeData {
  name: string;
  email: string;
  phone?: string;
  location?: string;
  skills: string[];
  technical_skills: string[];
  years_experience: number;
  summary?: string;
  experience: ExperienceItem[];
  education: EducationItem[];
}

export interface ExperienceItem {
  company: string;
  title: string;
  duration: string;
  highlights: string[];
}

export interface EducationItem {
  institution: string;
  degree: string;
  year: string;
}

export interface JobPreferences {
  job_title: string;
  location: string;
  salary_min?: number;
  salary_max?: number;
  job_type: 'full-time' | 'part-time' | 'contract';
  remote_preference: 'remote' | 'hybrid' | 'onsite' | 'any';
  platforms: string[];
  auto_apply: boolean;
  min_match_score: number;
}

export interface JobListing {
  title: string;
  company: string;
  location: string;
  salary_range?: string;
  url: string;
  platform: string;
  posted_date?: string;
  requirements?: string[];
  match_score?: number;
  matching_skills?: string[];
  skill_gaps?: string[];
  skill_gap_coaching?: string;
  recommended_keywords?: string[];
  cover_letter?: string;
  status?: ApplicationStatus;
  confirmation?: string;
}

export type ApplicationStatus =
  | 'discovered'
  | 'matched'
  | 'cover_letter_ready'
  | 'pending_review'
  | 'applying'
  | 'submitted'
  | 'confirmed'
  | 'rejected'
  | 'error'
  | 'requires_human';

export interface AgentMessage {
  type: string;
  message?: string;
  platform?: string;
  status?: string;
  count?: number;
  job_title?: string;
  company?: string;
  match_score?: number;
  progress?: string;
  requires_human?: boolean;
  devtools_url?: string;
  matched_jobs?: JobListing[];
  total_applications?: number;
  timestamp?: string;
}

export interface SearchResult {
  session_id: string;
  total_found: number;
  matched_count: number;
  message: string;
  matched_jobs: JobListing[];
}
