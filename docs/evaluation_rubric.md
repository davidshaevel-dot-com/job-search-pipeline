# Job Evaluation Rubric

This rubric is used by the job search pipeline to automatically evaluate discovered job opportunities. The evaluation is performed by Claude API using this standardized framework.

## Grading Scale
- **A (90-100)**: Excellent - Exceeds expectations, strong positive factor
- **B (80-89)**: Good - Meets expectations well, positive factor
- **C (70-79)**: Acceptable - Meets minimum expectations, neutral factor
- **D (60-69)**: Below Average - Concerning, negative factor
- **F (0-59)**: Poor - Major red flag, significant negative factor

## Evaluation Factors

### 1. Skills & Experience Match (Weight: 25%)
**Criteria:**
- How well do your technical skills align with the role requirements?
- Do you have relevant experience in the domain/industry?
- Can you hit the ground running vs. steep learning curve?

**Sub-factors:**
- Technical stack alignment
- Years of experience match
- Domain knowledge relevance
- Architecture/infrastructure experience

### 2. Compensation & Benefits (Weight: 20%)
**Criteria:**
- Base salary competitiveness for market and experience level
- Equity/stock options value and vesting schedule
- Health insurance, 401k, and standard benefits
- Bonus structure and performance incentives
- Total compensation package vs. market rate

**Sub-factors:**
- Base salary relative to market
- Equity potential and terms
- Benefits quality and comprehensiveness
- Additional perks (remote stipend, education, etc.)

### 3. Company Stability & Growth Potential (Weight: 15%)
**Criteria:**
- Funding status and runway
- Revenue/business model viability
- Market opportunity and competition
- Leadership team track record
- Product-market fit indicators

**Sub-factors:**
- Funding and financial health
- Business model strength
- Market size and opportunity
- Competitive positioning
- Leadership experience

### 4. Work-Life Balance (Weight: 15%)
**Criteria:**
- Expected working hours and on-call requirements
- Flexibility (remote work, flexible hours)
- PTO policy and actual usage
- Team culture around burnout prevention
- Meeting load and work intensity

**Sub-factors:**
- Remote/hybrid flexibility
- PTO and vacation policy
- After-hours expectations
- Company culture on boundaries

### 5. Career Growth & Learning (Weight: 10%)
**Criteria:**
- Opportunities to learn new technologies and skills
- Path for advancement and increasing responsibility
- Mentorship and professional development support
- Scope of impact and influence
- Resume value of the role

**Sub-factors:**
- Technical skill development
- Leadership opportunities
- Visibility and impact scope
- Industry recognition value

### 6. Company Culture & Values (Weight: 8%)
**Criteria:**
- Team collaboration and communication style
- Diversity and inclusion
- Transparency and trust
- Mission alignment with personal values
- Employee satisfaction and retention

**Sub-factors:**
- Team dynamics
- Company mission alignment
- Communication culture
- Employee engagement

### 7. Role Clarity & Expectations (Weight: 5%)
**Criteria:**
- Clear definition of responsibilities
- Realistic expectations for deliverables
- Well-defined success metrics
- Organizational structure clarity
- Reporting relationships

**Sub-factors:**
- Job description clarity
- Success metrics definition
- Team structure
- Autonomy vs. direction

### 8. Location & Commute (Weight: 2%)
**Criteria:**
- Office location and commute time
- Remote work options
- In-office requirements
- Relocation needs

**Sub-factors:**
- Physical office location
- Remote flexibility
- Travel requirements

---

## Overall Grade Calculation

**Formula:**
```
Overall Grade = (Skills Match × 0.25) + (Compensation × 0.20) + (Stability × 0.15) +
                (Work-Life × 0.15) + (Growth × 0.10) + (Culture × 0.08) +
                (Role Clarity × 0.05) + (Location × 0.02)
```

**Overall Grade Interpretation:**
- **A (90-100)**: Exceptional opportunity - Strongly pursue
- **B (80-89)**: Strong opportunity - Definitely pursue
- **C (70-79)**: Acceptable opportunity - Consider carefully
- **D (60-69)**: Questionable opportunity - Significant concerns
- **F (0-59)**: Poor opportunity - Do not pursue

---

## Decision Framework

### Grade A: Strongly Pursue
- Prepare tailored resume and cover letter
- Research extensively for interviews
- Express high interest to recruiter
- Prioritize interview scheduling
- Auto-create Linear issue (if enabled)

### Grade B: Definitely Pursue
- Prepare tailored resume
- Express interest to recruiter
- Schedule interview when convenient
- Continue evaluating other opportunities
- Auto-create Linear issue (if enabled)

### Grade C: Consider Carefully
- Gather more information before deciding
- Ask clarifying questions to recruiter
- Compare with other opportunities
- May pursue if limited options
- Manual review recommended

### Grade D-F: Do Not Pursue
- Politely decline or deprioritize
- Provide feedback to recruiter if appropriate
- Focus energy on better opportunities
- Archive opportunity

---

## Usage in Pipeline

This rubric is used by the AI evaluation engine (`src/evaluation/ai_evaluator.py`) to automatically score discovered job opportunities. The evaluation prompt includes this rubric and asks Claude to:

1. Score each factor (0-100)
2. Provide brief justification for each score
3. Calculate overall weighted score
4. Assign grade (A/B/C/D/F)
5. Provide recommendation (Strongly Pursue / Pursue / Consider / Skip)
6. List key strengths and concerns

The evaluation results are stored with each job opportunity and used to determine:
- Whether to create a Linear issue automatically
- Whether to send Slack notifications
- How to organize the opportunity in the folder structure

---

**Last Updated:** November 8, 2025  
**Used By:** Job Search Pipeline AI Evaluation Engine

