import uvicorn
#from assistant_core.main import app

if __name__ == "__main__":
    uvicorn.run("assistant_core.main:app", host="127.0.0.1", port=8000,reload=True)