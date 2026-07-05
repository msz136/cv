# Supported Roles

This tool ships with 4 well-tuned roles. Each has its own scoring criteria, weighted areas, and test cases.

For roles not listed here, the tool falls back to the shared rules in `scoring-heuristics.md` and adapts from the JD. Results for roles we don't cover will be less exact.

## Launch Roles

### 1. Product Management
Covers: Product Manager, Senior PM, Group PM, Product Owner, Director of Product.
Does NOT cover: Technical PM (use Eng or AI PM criteria based on context), Growth PM (use PM criteria but weight Growth work higher).
Criteria file: `role-criteria/product-management.md`

### 2. AI / ML Product Management
Covers: AI PM, ML PM, AI Product Manager, Product Manager for AI/ML platforms.
This is a distinct role from normal PM. It needs different scoring criteria, signals, and tuning.
Criteria file: `role-criteria/ai-product-management.md`

### 3. Software Engineering
Covers: Software Engineer, Senior Engineer, Staff Engineer, Backend/Frontend/Full-stack Engineer, Engineering Manager (technical track).
Does NOT cover: DevOps/SRE (close but different focus), QA/Test Eng, Security Eng.
Criteria file: `role-criteria/engineering.md`

### 4. Business Analysis / BSA
Covers: Business Analyst, Business Systems Analyst (BSA), Senior BA, Lead BA, Requirements Analyst, Systems Analyst.
Does NOT cover: Product Analyst (closer to PM criteria), Data Analyst (planned future role).
Criteria file: `role-criteria/business-analysis.md`

## Unsupported Roles (Planned)

These roles are on the roadmap. Help from the community is welcome. See CONTRIBUTING.md for how to add a new role.

- Data Science / Analytics
- Design (UX/UI, Product Design)
- Marketing (Growth, Product Marketing, Demand Gen)
- Sales (AE, SDR/BDR, Sales Engineering)
- Operations (Program Management, Business Operations)
- Finance (FP&A, Corporate Development)

## How to Pick Which Role Applies

1. Read the job title and post
2. If the JD mentions AI/ML products, model work, or eval setups, use **AI PM** criteria even if the title just says "Product Manager"
3. If the JD is unclear between two roles, state the overlap and score against both. Show both scores with a note
4. If the role doesn't match any we support, say so clearly. Use the shared rules and flag that scoring is less exact
