# 🏗️ **Complete User Guide: Lumber Estimator System**

## **📋 Table of Contents**
1. [System Overview](#system-overview)
2. [Getting Started](#getting-started)
3. [Step-by-Step PDF Upload & Estimation](#step-by-step-pdf-upload--estimation)
4. [Viewing Estimation Results](#viewing-estimation-results)
5. [Understanding Accuracy Metrics](#understanding-accuracy-metrics)
6. [Downloading Estimation Reports](#downloading-estimation-reports)
7. [Checking System Accuracy](#checking-system-accuracy)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## **🚀 System Overview**

Your Lumber Estimator is an AI-powered system that:
- **Analyzes architectural PDFs** using Google Gemini 2.0 Flash
- **Extracts materials and quantities** automatically
- **Matches to lumber database** for accurate pricing
- **Provides confidence metrics** for every estimation
- **Generates professional reports** for client delivery

---

## **🔧 Getting Started**

### **Prerequisites**
- ✅ Lumber Estimator system running on port 8003
- ✅ Valid user account with authentication
- ✅ Architectural PDF files ready for upload
- ✅ Web browser or API client (Postman, curl, etc.)

### **Access Points**
- **Main API**: `http://localhost:8003`
- **Interactive Documentation**: `http://localhost:8003/docs`
- **Health Check**: `http://localhost:8003/health`

---

## **📄 Step-by-Step PDF Upload & Estimation**

### **Step 1: Start the System**
```bash
# Navigate to your project directory
cd "path/to/your/lumber-estimator"

# Start the server
python app.py
```

**Expected Output:**
```
🚀 Starting Lumber Estimator API Server...
📖 API Documentation: http://localhost:8003/docs
🔧 Health Check: http://localhost:8003/health
```

### **Step 2: Verify System Health**
```bash
# Check if system is running
curl http://localhost:8003/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### **Step 3: Authenticate (Get Access Token)**
```bash
# Login to get access token
curl -X POST "http://localhost:8003/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Save the access token** from the response for subsequent requests.

### **Step 4: Upload PDF for Lumber Estimation**
```bash
# Upload PDF and get lumber estimation
curl -X POST "http://localhost:8003/lumber/estimate/pdf" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@your_architectural_drawing.pdf" \
  -F "project_name=My House Project" \
  -F "force_fresh=false"
```

**Parameters Explained:**
- `file`: Your PDF file (max 50MB)
- `project_name`: Name for organizing your project
- `force_fresh`: `false` uses cached results, `true` forces new analysis

---

## **📊 Viewing Estimation Results**

### **Step 5: Analyze the Response**

Your system will return a comprehensive response like this:

```json
{
  "success": true,
  "message": "Lumber estimation from PDF completed successfully",
  "project_name": "My House Project",
  "pdf_filename": "your_architectural_drawing.pdf",
  "analysis_timestamp": "2025-01-15T10:30:00Z",
  "accuracy_metrics": {
    "overall_accuracy": 87.5,
    "confidence_level": "high",
    "confidence_interval": [84.2, 90.8],
    "material_accuracy": {
      "Walls": 92.3,
      "Joist": 87.1,
      "Roof": 91.5
    },
    "total_items": 45,
    "matched_items": 42,
    "unmatched_items": 3,
    "validation_notes": [
      "Good estimation accuracy - results are reliable",
      "3 items require manual quotation or verification"
    ]
  },
  "results": {
    "project_info": {
      "project_name": "My House Project",
      "pdf_filename": "your_architectural_drawing.pdf",
      "analysis_date": "2025-01-15T10:30:00Z",
      "extraction_method": "AI-powered PDF analysis"
    },
    "building_dimensions": {
      "length_feet": 40,
      "width_feet": 30,
      "height_feet": 8,
      "area_sqft": 1200
    },
    "summary": {
      "total_materials_detected": 45,
      "lumber_materials_matched": 42,
      "total_estimated_cost": 15423.45,
      "items_needing_quotation": 3
    },
    "detailed_items": [
      {
        "extracted_item": {
          "item_name": "2X4X8 KD H-FIR STD&BTR",
          "category": "Walls",
          "dimensions": "2x4x8",
          "location": "Wall framing",
          "quantity": 45,
          "unit": "each"
        },
        "database_match": {
          "item_id": 1,
          "description": "2X4X8 KD H-FIR STD&BTR",
          "category": "Walls",
          "subcategory": "Studs",
          "dimensions": "2x4x8",
          "material": "H-FIR",
          "grade": "STD&BTR",
          "unit_price": 5.71,
          "unit": "each"
        },
        "quantity_needed": 45,
        "total_cost": 256.95,
        "match_confidence": "high",
        "available_contractors": ["ABC Supply", "XYZ Lumber"],
        "recommended_contractor": "ABC Supply",
        "material_type": "lumber",
        "notes": "Matched to database item: 2X4X8 KD H-FIR STD&BTR"
      }
    ],
    "lumber_estimates": {
      "total_lumber_cost": 15423.45,
      "lumber_by_category": {
        "Walls": {
          "total_quantity": 120,
          "total_cost": 6840.00,
          "items": [...]
        },
        "Joist": {
          "total_quantity": 85,
          "total_cost": 4230.00,
          "items": [...]
        },
        "Roof": {
          "total_quantity": 65,
          "total_cost": 4353.45,
          "items": [...]
        }
      }
    }
  }
}
```

---

## **🎯 Understanding Accuracy Metrics**

### **Step 6: Interpret Accuracy Results**

#### **Overall Accuracy Score**
- **87.5%** = High confidence, reliable for bidding
- **Confidence Level**: "high" (85-94% range)
- **Confidence Interval**: 84.2% - 90.8% (95% statistical confidence)

#### **Material Category Accuracy**
- **Walls**: 92.3% (Excellent)
- **Joist**: 87.1% (Good)
- **Roof**: 91.5% (Excellent)

#### **Item Breakdown**
- **Total Items**: 45 materials detected
- **Matched Items**: 42 successfully matched to database
- **Unmatched Items**: 3 require manual quotation

#### **Validation Notes**
- ✅ "Good estimation accuracy - results are reliable"
- ⚠️ "3 items require manual quotation or verification"

---

## **📥 Downloading Estimation Reports**

### **Step 7: Download Complete Estimation Report**

#### **Option A: Download via API**
```bash
# Download the estimation report
curl -X GET "http://localhost:8003/lumber/estimate/pdf" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@your_architectural_drawing.pdf" \
  -F "project_name=My House Project" \
  --output "estimation_report.json"
```

#### **Option B: Access Saved Files**
The system automatically saves results to:
```
outputs/lumber_pdf_estimates/
├── My House Project_pdf_analysis_20250115_103000.json
└── ...
```

### **Step 8: Generate PDF Report (Manual)**

Since the system outputs JSON, you can convert to PDF using:

```python
# Example Python script to convert JSON to PDF
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def json_to_pdf(json_file, pdf_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Add title
    story.append(Paragraph(f"Lumber Estimation Report: {data['project_name']}", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Add accuracy metrics
    accuracy = data['accuracy_metrics']
    story.append(Paragraph(f"Overall Accuracy: {accuracy['overall_accuracy']}%", styles['Heading1']))
    story.append(Paragraph(f"Confidence Level: {accuracy['confidence_level']}", styles['Normal']))
    
    # Add material breakdown
    story.append(Spacer(1, 12))
    story.append(Paragraph("Material Breakdown", styles['Heading2']))
    
    # Continue building the PDF...
    
    doc.build(story)

# Usage
json_to_pdf("estimation_report.json", "lumber_estimation_report.pdf")
```

---

## **📊 Checking System Accuracy**

### **Step 9: View Overall System Accuracy**

#### **Get Accuracy Summary**
```bash
curl -X GET "http://localhost:8003/accuracy/summary" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "total_estimates": 25,
  "recent_estimates": 10,
  "average_accuracy": 87.5,
  "accuracy_trend": "improving",
  "best_accuracy": 95.2,
  "worst_accuracy": 62.1,
  "recent_accuracy": [89.2, 87.5, 91.3, 85.7, 88.9]
}
```

#### **Validate Specific PDF Accuracy**
```bash
curl -X POST "http://localhost:8003/accuracy/validate/pdf" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@your_architectural_drawing.pdf"
```

### **Step 10: Export Accuracy Reports**

#### **Download Comprehensive Accuracy Report**
```bash
curl -X GET "http://localhost:8003/accuracy/report" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --output "accuracy_report.json"
```

---

## **🔍 Complete Workflow Example**

### **Full Example: House Project Estimation**

```bash
# 1. Start system
python app.py

# 2. Check health
curl http://localhost:8003/health

# 3. Login and get token
TOKEN=$(curl -s -X POST "http://localhost:8003/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}' \
  | jq -r '.access_token')

# 4. Upload PDF for estimation
curl -X POST "http://localhost:8003/lumber/estimate/pdf" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@house_plans.pdf" \
  -F "project_name=Dream House Project" \
  --output "estimation_result.json"

# 5. Check accuracy summary
curl -X GET "http://localhost:8003/accuracy/summary" \
  -H "Authorization: Bearer $TOKEN"

# 6. Download accuracy report
curl -X GET "http://localhost:8003/accuracy/report" \
  -H "Authorization: Bearer $TOKEN" \
  --output "accuracy_report.json"
```

---

## **⚠️ Troubleshooting**

### **Common Issues & Solutions**

#### **1. System Won't Start**
```bash
# Check if port 8003 is available
netstat -an | grep 8003

# Kill process using port 8003
lsof -ti:8003 | xargs kill -9

# Restart system
python app.py
```

#### **2. Authentication Errors**
```bash
# Verify token is valid
curl -X GET "http://localhost:8003/health" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Re-login if token expired
curl -X POST "http://localhost:8003/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

#### **3. PDF Upload Fails**
```bash
# Check file size (max 50MB)
ls -lh your_file.pdf

# Verify PDF format
file your_file.pdf

# Check system logs
tail -f logs/app.log
```

#### **4. Low Accuracy Results**
- **Use higher quality PDFs** with clear text
- **Include detailed specifications** and quantities
- **Check database coverage** for missing materials
- **Review validation notes** for improvement tips

---

## **💡 Best Practices**

### **For Best Results:**

#### **PDF Quality**
- ✅ **Use vector PDFs** (not scanned images)
- ✅ **Include material schedules** and specifications
- ✅ **Show quantity callouts** clearly
- ✅ **Provide building dimensions** and dimensions
- ✅ **Use multiple drawing sheets** for comprehensive coverage

#### **Project Organization**
- ✅ **Use descriptive project names** for easy identification
- ✅ **Group related PDFs** by project
- ✅ **Track accuracy trends** over time
- ✅ **Export reports regularly** for record keeping

#### **Accuracy Monitoring**
- ✅ **Check accuracy metrics** for every estimation
- ✅ **Review validation notes** for improvements
- ✅ **Monitor system trends** weekly
- ✅ **Use accuracy reports** for client confidence

---

## **📱 Alternative: Using the Web Interface**

### **Step-by-Step Web Interface Usage**

1. **Open Browser**: Navigate to `http://localhost:8003/docs`
2. **Authenticate**: Click "Authorize" and enter your credentials
3. **Upload PDF**: Use the `/lumber/estimate/pdf` endpoint
4. **View Results**: See estimation and accuracy metrics
5. **Download Reports**: Use export endpoints for data

---

## **🎯 Quick Reference Commands**

### **Essential Commands**
```bash
# Start system
python app.py

# Check health
curl http://localhost:8003/health

# Upload PDF for estimation
curl -X POST "http://localhost:8003/lumber/estimate/pdf" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@your_file.pdf" \
  -F "project_name=Project Name"

# Check accuracy
curl -X GET "http://localhost:8003/accuracy/summary" \
  -H "Authorization: Bearer $TOKEN"

# Download accuracy report
curl -X GET "http://localhost:8003/accuracy/report" \
  -H "Authorization: Bearer $TOKEN" \
  --output "report.json"
```

---

## **🎉 Success Indicators**

### **When Everything Works:**
- ✅ System starts without errors
- ✅ Health check returns "healthy"
- ✅ PDF upload completes successfully
- ✅ Accuracy metrics are displayed
- ✅ Reports can be downloaded
- ✅ Confidence levels are "high" or "very high"

### **What to Expect:**
- **High-quality PDFs**: 85-95% accuracy
- **Medium-quality PDFs**: 70-84% accuracy
- **Low-quality PDFs**: Below 70% accuracy (manual review needed)

---

**🎯 This guide covers the complete workflow from PDF upload to accuracy analysis. Your system now provides transparent, reliable lumber estimations with confidence metrics that users can trust!**







