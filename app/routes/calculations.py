from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.calculation_factory import CalculationFactory
from app.database import get_db
from app.models.calculation import Calculation
from app.schemas.calculation import CalculationCreate, CalculationRead

router = APIRouter(prefix="/calculations", tags=["Calculations"])


def get_calculation_or_404(db: Session, calculation_id: int) -> Calculation:
    calculation = db.get(Calculation, calculation_id)
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found.")
    return calculation


@router.get("", response_model=list[CalculationRead])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).order_by(Calculation.id).all()


@router.get("/{calculation_id}", response_model=CalculationRead)
def read_calculation(calculation_id: int, db: Session = Depends(get_db)):
    return get_calculation_or_404(db, calculation_id)


@router.post("", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def add_calculation(payload: CalculationCreate, db: Session = Depends(get_db)):
    calculation = Calculation(
        a=payload.a,
        b=payload.b,
        type=payload.type.value,
        result=CalculationFactory.calculate(payload),
    )
    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation


@router.put("/{calculation_id}", response_model=CalculationRead)
def edit_calculation(
    calculation_id: int,
    payload: CalculationCreate,
    db: Session = Depends(get_db),
):
    calculation = get_calculation_or_404(db, calculation_id)
    calculation.a = payload.a
    calculation.b = payload.b
    calculation.type = payload.type.value
    calculation.result = CalculationFactory.calculate(payload)

    db.commit()
    db.refresh(calculation)
    return calculation


@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(calculation_id: int, db: Session = Depends(get_db)):
    calculation = get_calculation_or_404(db, calculation_id)
    db.delete(calculation)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)