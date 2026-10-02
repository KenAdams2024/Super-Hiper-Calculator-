import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, 
    standard_transformations, 
    implicit_multiplication_application, 
    convert_xor
)

app = FastAPI(title="Super HiPER Backend")

# Allow seamless frontend communication cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom mapping array to transform visual input layouts cleanly into standard text-parse math
transformations = standard_transformations + (implicit_multiplication_application, convert_xor)

class CalculationRequest(BaseModel):
    expression: str
    precision: int = Field(default=100, ge=1, le=1000)

@app.post("/api/compute")
def compute_math(req: CalculationRequest):
    try:
        # Pre-process human inputs safely to map structural notation anomalies
        sanitized = req.expression.replace("√", "sqrt")
        sanitized = sanitized.replace("π", "pi")
        
        # Parse expression tree with mathematical engine definitions
        parsed_expr = parse_expr(sanitized, transformations=transformations)
        
        # Resolve exact symbolic answer forms
        symbolic_result = sp.simplify(parsed_expr)
        
        # Calculate matching numerical floating string using arbitrary scale constraints
        numerical_result = symbolic_result.evalf(n=req.precision)
        
        return {
            "status": "success",
            "latex_output": sp.latex(symbolic_result),
            "numerical_output": str(numerical_result)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Connect to static layout interface definitions safely
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
