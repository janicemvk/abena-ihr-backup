import uvicorn

if __name__ == "__main__":
    print("Starting Abena IHR Presentation Layer...")
    print("Access the telemedicine UI at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "presentation_layer:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )  