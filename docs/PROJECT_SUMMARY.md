# Vantage RWE - Project Summary

**Commercial Intelligence from Real-World Evidence**

## 🎯 Project Overview

The OMOP Cohort Builder is a full-stack web application that enables healthcare researchers and data analysts to interactively create patient cohorts from healthcare data stored in the OHDSI OMOP Common Data Model (CDM) format within Databricks. The application combines traditional point-and-click cohort building with modern GenAI-powered natural language query capabilities.

## ✨ Key Features

### 1. Interactive Cohort Building
- **Visual Interface**: Drag-and-drop style cohort definition
- **Multiple Criteria Types**: Conditions, drugs, procedures, visits, observations
- **Flexible Logic**: Combine inclusion and exclusion criteria
- **Real-time Preview**: See patient counts as you build
- **Date Ranges**: Filter by occurrence dates
- **Minimum Occurrences**: Require multiple instances of conditions/treatments

### 2. GenAI Natural Language Queries
- **Ask Questions**: "Show me patients with diabetes on metformin"
- **Automatic Translation**: Converts natural language to cohort criteria
- **SQL Generation**: See the generated SQL queries
- **Instant Results**: Get patient counts and demographics
- **Learning Tool**: Understand how queries map to OMOP concepts

### 3. OMOP CDM Integration
- **Concept Search**: Search across SNOMED, RxNorm, ICD-10, etc.
- **Standardized Vocabularies**: Use standard medical terminologies
- **Complete Coverage**: Access all OMOP clinical domains
- **Hierarchy Support**: Leverage concept relationships

### 4. Rich Results & Analytics
- **Patient Counts**: See total patients matching criteria
- **Demographics**: Age and gender distributions
- **Sample IDs**: Preview specific patient identifiers
- **Export Options**: Download patient lists and cohort definitions

### 5. Databricks Native
- **Scalable Queries**: Leverage Databricks compute power
- **SQL Warehouse**: Use serverless or provisioned warehouses
- **Unity Catalog**: Support for data governance
- **Performance**: Optimized SQL generation for large datasets

## 📁 Project Structure

```
omop/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   └── routes.py      # REST API routes
│   │   ├── db/                # Database layer
│   │   │   └── databricks.py  # Databricks connector
│   │   ├── models/            # Data models
│   │   │   └── cohort.py      # Pydantic models
│   │   ├── services/          # Business logic
│   │   │   ├── cohort_builder.py
│   │   │   ├── genai_service.py
│   │   │   └── omop_service.py
│   │   ├── config.py          # Configuration
│   │   └── main.py            # FastAPI app
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example          # Environment template
│   └── test_connection.py    # Connection test script
│
├── frontend/                  # React Frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── CohortBuilder.tsx
│   │   │   ├── CriteriaBuilder.tsx
│   │   │   ├── CohortResults.tsx
│   │   │   ├── NaturalLanguageSearch.tsx
│   │   │   └── DatabaseStats.tsx
│   │   ├── services/         # API client
│   │   │   └── api.ts
│   │   ├── App.tsx           # Main app component
│   │   ├── App.css
│   │   ├── index.tsx
│   │   └── index.css
│   ├── package.json          # Node dependencies
│   ├── tsconfig.json         # TypeScript config
│   └── .env.example         # Environment template
│
├── README.md                 # Project overview
├── QUICKSTART.md            # Quick start guide
├── SETUP_GUIDE.md           # Detailed setup
├── ARCHITECTURE.md          # Technical architecture
├── EXAMPLE_COHORTS.md       # Example cohort definitions
├── run_dev.sh               # Development runner script
└── .gitignore               # Git ignore rules
```

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI 0.109
- **Language**: Python 3.9+
- **Database**: Databricks SQL Connector
- **Validation**: Pydantic
- **API Docs**: Swagger/OpenAPI

### Frontend
- **Framework**: React 18.2
- **Language**: TypeScript
- **HTTP Client**: Axios
- **Build Tool**: Create React App
- **Styling**: CSS Modules

### Data Platform
- **Database**: Databricks
- **Data Model**: OHDSI OMOP CDM v5.4
- **Compute**: SQL Warehouse or Cluster
- **Storage**: Delta Lake

## 🚀 Quick Start

### 1. Setup (5 minutes)
```bash
# Configure Databricks
cp backend/.env.example backend/.env
# Edit with your credentials

# Install dependencies
cd backend && pip install -r requirements.txt && cd ..
cd frontend && npm install && cd ..
```

### 2. Test Connection
```bash
cd backend
python test_connection.py
```

### 3. Run Application
```bash
# Option 1: Use the runner script
./run_dev.sh

# Option 2: Manual start
# Terminal 1:
cd backend && uvicorn app.main:app --reload

# Terminal 2:
cd frontend && npm start
```

### 4. Access
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 Example Use Cases

### Clinical Research
- **Patient Recruitment**: Identify eligible patients for clinical trials
- **Cohort Characterization**: Understand patient populations
- **Treatment Patterns**: Analyze medication usage across conditions
- **Outcomes Analysis**: Track patient outcomes by treatment

### Population Health
- **Disease Surveillance**: Monitor disease prevalence and incidence
- **Quality Measures**: Calculate quality metrics for patient populations
- **Risk Stratification**: Identify high-risk patient groups
- **Care Gaps**: Find patients missing recommended care

### Real-World Evidence
- **Comparative Effectiveness**: Compare treatment outcomes
- **Safety Surveillance**: Monitor adverse events
- **Drug Utilization**: Analyze medication patterns
- **Healthcare Utilization**: Study visit and procedure patterns

## 🎓 Learning Resources

### Documentation
- `README.md` - High-level overview
- `QUICKSTART.md` - Get started in 5 minutes
- `SETUP_GUIDE.md` - Detailed installation guide
- `ARCHITECTURE.md` - Technical deep dive
- `EXAMPLE_COHORTS.md` - Sample cohort definitions

### OMOP Resources
- [OHDSI Website](https://www.ohdsi.org/)
- [OMOP CDM Documentation](https://ohdsi.github.io/CommonDataModel/)
- [ATHENA Vocabulary Browser](https://athena.ohdsi.org/)
- [OHDSI Forums](https://forums.ohdsi.org/)

### Databricks Resources
- [Databricks SQL Documentation](https://docs.databricks.com/sql/)
- [Databricks GenAI](https://docs.databricks.com/generative-ai/)
- [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/)

## 🔒 Security & Compliance

### Authentication & Authorization
- Databricks personal access tokens
- Token-based API authentication
- Inherited Databricks table permissions
- CORS configuration for API access

### Data Privacy
- No patient data stored in application
- All queries executed in Databricks
- Results returned in memory only
- Patient IDs can be de-identified

### Compliance Considerations
- HIPAA: Use Databricks HIPAA-eligible workspace
- GDPR: Implement data access controls
- Audit Logging: Track all cohort queries
- Data Governance: Use Unity Catalog

## 🔄 Development Workflow

### Backend Development
```bash
cd backend
source venv/bin/activate  # If using venv
uvicorn app.main:app --reload
# Edit files in app/
# API auto-reloads on changes
```

### Frontend Development
```bash
cd frontend
npm start
# Edit files in src/
# Hot reload enabled
```

### Adding New Features

**New Criteria Type:**
1. Add to `CriteriaType` enum in `backend/app/models/cohort.py`
2. Implement SQL builder in `backend/app/services/cohort_builder.py`
3. Add UI option in `frontend/src/components/CriteriaBuilder.tsx`

**New API Endpoint:**
1. Define route in `backend/app/api/routes.py`
2. Add service logic in appropriate service file
3. Update API client in `frontend/src/services/api.ts`
4. Create/update React component

## 📈 Performance Considerations

### Query Optimization
- Use concept sets instead of individual IDs
- Add date filters to reduce data scanned
- Leverage Databricks query caching
- Consider materialized views for common queries

### Scaling
- Backend: Stateless design, horizontally scalable
- Frontend: Static build, deploy to CDN
- Database: Use Databricks auto-scaling
- Caching: Add Redis for concept search results

## 🐛 Troubleshooting

### Common Issues

**Connection Failed**
- Check Databricks credentials
- Verify SQL Warehouse is running
- Test with `test_connection.py`

**No Search Results**
- Verify concept table is populated
- Check domain filters
- Try different search terms

**Slow Queries**
- Add date range filters
- Use smaller concept sets
- Check Databricks warehouse size

**Frontend Build Errors**
- Delete `node_modules` and reinstall
- Clear npm cache
- Check Node.js version

## 🚢 Deployment Options

### Production - Databricks Apps (Recommended)
- Deploy as Databricks App
- Single platform deployment
- Built-in authentication and OAuth
- Simplified management
- Auto-scaling via SQL Warehouse
- No infrastructure management

### Development - Local
- Local backend + frontend
- Direct Databricks connection
- Hot reload for rapid development
- Same OAuth authentication as production

### Production - Cloud (Alternative)
- Backend: AWS Lambda / Azure Functions / GCP Cloud Run
- Frontend: Vercel / Netlify / S3 + CloudFront
- Database: Databricks (existing)
- More complex setup and management

### Enterprise - Custom
- Kubernetes deployment
- API Gateway
- Load balancing
- Advanced monitoring & alerting
- Custom security requirements

## 🎯 Next Steps & Extensions

### Short Term
- [ ] Add cohort save/load functionality
- [ ] Export to CSV/Excel
- [ ] More demographics visualizations
- [ ] Query history

### Medium Term
- [ ] User authentication
- [ ] Cohort versioning
- [ ] Collaboration features
- [ ] Advanced statistics

### Long Term
- [ ] AI-powered cohort suggestions
- [ ] Temporal logic (before/after relationships)
- [ ] Survival analysis
- [ ] Propensity score matching
- [ ] Integration with Databricks ML

## 👥 Contributing

This is a prototype/demo application. To extend:

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Update documentation
5. Submit pull request

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- **OHDSI Community**: For OMOP CDM standard
- **Databricks**: For the data platform
- **FastAPI**: For the excellent web framework
- **React Team**: For the UI framework

## 📧 Support

For questions or issues:
1. Check documentation files
2. Review API docs at `/docs`
3. Test connection with `test_connection.py`
4. Check Databricks logs
5. Review application logs

---

**Built with ❤️ for the healthcare data community**

Version: 1.0.0 (Prototype)
Last Updated: December 2024

