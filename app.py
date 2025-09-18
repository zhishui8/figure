"""Main Flask application for the couple budgeting web app."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Iterable, Tuple

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------


def create_app() -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__)
    app.config.setdefault("SECRET_KEY", "change-me")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///couple_budget.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    register_filters(app)
    register_routes(app)
    return app


db = SQLAlchemy()


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    partner = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # "income" or "expense"
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=False, default=date.today)

    def as_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "partner": self.partner,
            "type": self.type,
            "category": self.category,
            "amount": float(self.amount),
            "description": self.description or "",
            "date": self.date.strftime("%Y-%m-%d"),
        }


PARTNER_CHOICES: Tuple[Tuple[str, str], ...] = (
    ("partner_a", "Ta 1"),
    ("partner_b", "Ta 2"),
)

CATEGORY_SUGGESTIONS: Tuple[str, ...] = (
    "餐饮",
    "住房",
    "交通",
    "娱乐",
    "礼物",
    "旅行",
    "储蓄",
)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def _to_decimal(amount: str) -> Decimal:
    try:
        return Decimal(amount)
    except Exception as exc:  # pragma: no cover - defensive fallback
        raise ValueError("金额格式不正确") from exc


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("日期格式不正确") from exc


# ---------------------------------------------------------------------------
# Template filters
# ---------------------------------------------------------------------------


def register_filters(app: Flask) -> None:
    @app.template_filter("currency")
    def currency_filter(value: object) -> str:
        try:
            return f"{Decimal(value):,.2f}"
        except Exception:  # pragma: no cover - formatting fallback
            return str(value)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


def register_routes(app: Flask) -> None:
    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            try:
                partner = request.form.get("partner")
                entry_type = request.form.get("type")
                category = request.form.get("category", "").strip()
                amount = _to_decimal(request.form.get("amount", "0"))
                description = request.form.get("description", "").strip() or None
                entry_date = _parse_date(request.form.get("date", date.today().isoformat()))
            except ValueError as err:
                flash(str(err), "error")
                return redirect(url_for("index"))

            if partner not in dict(PARTNER_CHOICES):
                flash("请选择有效的参与者", "error")
                return redirect(url_for("index"))

            if entry_type not in {"income", "expense"}:
                flash("收支类型无效", "error")
                return redirect(url_for("index"))

            if not category:
                flash("请填写分类", "error")
                return redirect(url_for("index"))

            if entry_type == "expense" and amount <= 0:
                flash("支出金额必须大于0", "error")
                return redirect(url_for("index"))

            if entry_type == "income" and amount <= 0:
                flash("收入金额必须大于0", "error")
                return redirect(url_for("index"))

            transaction = Transaction(
                partner=partner,
                type=entry_type,
                category=category,
                amount=amount,
                description=description,
                date=entry_date,
            )
            db.session.add(transaction)
            db.session.commit()
            flash("账目添加成功", "success")
            return redirect(url_for("index"))

        transactions = Transaction.query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()

        totals = calculate_totals(transactions)
        partner_labels = [label for _, label in PARTNER_CHOICES]
        partner_keys = [key for key, _ in PARTNER_CHOICES]
        partner_summary = totals["partners"]
        partner_income_series = [
            float(partner_summary.get(key, {}).get("income", Decimal("0")))
            for key in partner_keys
        ]
        partner_expense_series = [
            float(partner_summary.get(key, {}).get("expense", Decimal("0")))
            for key in partner_keys
        ]
        monthly_chart = {
            "labels": [item["month"] for item in totals["monthly"]],
            "income": [float(item["income"]) for item in totals["monthly"]],
            "expense": [float(item["expense"]) for item in totals["monthly"]],
            "net": [float(item["net"]) for item in totals["monthly"]],
        }

        category_chart = {
            "labels": [name for name, _ in totals["categories"]],
            "values": [float(amount) for _, amount in totals["categories"]],
        }

        context = {
            "transactions": transactions,
            "partner_choices": PARTNER_CHOICES,
            "category_suggestions": CATEGORY_SUGGESTIONS,
            "total_income": totals["income"],
            "total_expense": totals["expense"],
            "net_total": totals["income"] - totals["expense"],
            "partner_summary": partner_summary,
            "partner_income_series": partner_income_series,
            "partner_expense_series": partner_expense_series,
            "partner_labels": partner_labels,
            "category_breakdown": totals["categories"],
            "monthly_totals": totals["monthly"],
            "monthly_chart": monthly_chart,
            "category_chart": category_chart,
            "today": date.today(),
        }
        return render_template("index.html", **context)

    @app.route("/delete/<int:transaction_id>", methods=["POST"])
    def delete_transaction(transaction_id: int):
        transaction = Transaction.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()
        flash("已删除账目", "success")
        return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Aggregation logic
# ---------------------------------------------------------------------------


def calculate_totals(transactions: Iterable[Transaction]) -> Dict[str, object]:
    total_income = Decimal("0")
    total_expense = Decimal("0")
    partner_totals: Dict[str, Dict[str, Decimal]] = defaultdict(
        lambda: {"income": Decimal("0"), "expense": Decimal("0")}
    )
    category_totals: Dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    monthly_totals: Dict[str, Dict[str, Decimal]] = defaultdict(
        lambda: {"income": Decimal("0"), "expense": Decimal("0")}
    )

    for entry in transactions:
        amount = Decimal(entry.amount)
        month_label = entry.date.strftime("%Y-%m")
        monthly_totals[month_label][entry.type] += amount

        if entry.type == "income":
            total_income += amount
            partner_totals[entry.partner]["income"] += amount
        else:
            total_expense += amount
            category_totals[entry.category] += amount
            partner_totals[entry.partner]["expense"] += amount

    ordered_monthly = sorted(monthly_totals.items(), key=lambda item: item[0])
    monthly_data = [
        {
            "month": month,
            "income": values["income"],
            "expense": values["expense"],
            "net": values["income"] - values["expense"],
        }
        for month, values in ordered_monthly
    ]

    ordered_categories = sorted(category_totals.items(), key=lambda item: item[1], reverse=True)

    partner_summary = {
        partner: {
            "income": values["income"],
            "expense": values["expense"],
            "net": values["income"] - values["expense"],
        }
        for partner, values in partner_totals.items()
    }

    return {
        "income": total_income,
        "expense": total_expense,
        "partners": partner_summary,
        "categories": ordered_categories,
        "monthly": monthly_data,
    }


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
