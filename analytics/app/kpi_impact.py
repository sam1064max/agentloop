from typing import Dict, Any


class KPIImpactCalculator:
    def resolution_to_savings(
        self, resolution_delta: float, monthly_volume: int, cost_per_resolution: float
    ) -> Dict[str, Any]:
        if monthly_volume < 0 or cost_per_resolution < 0:
            return {"error": "monthly_volume and cost_per_resolution must be non-negative"}

        resolution_rate_change = resolution_delta / 100.0
        additional_resolutions = int(round(monthly_volume * resolution_rate_change))
        monthly_savings = round(additional_resolutions * cost_per_resolution, 2)
        annual_savings = round(monthly_savings * 12, 2)

        return {
            "resolution_delta_pct": resolution_delta,
            "resolution_rate_change": round(resolution_rate_change, 4),
            "monthly_volume": monthly_volume,
            "cost_per_resolution": cost_per_resolution,
            "additional_resolutions": additional_resolutions,
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings,
            "currency": "USD",
        }

    def csat_to_revenue(
        self, csat_delta: float, customer_clv: float, monthly_active: int
    ) -> Dict[str, Any]:
        if customer_clv < 0 or monthly_active < 0:
            return {"error": "customer_clv and monthly_active must be non-negative"}

        csat_change = csat_delta / 100.0
        retention_lift = csat_change * 0.3
        additional_retained = int(round(monthly_active * retention_lift))
        monthly_revenue = round(additional_retained * customer_clv / 12, 2)
        annual_revenue = round(additional_retained * customer_clv, 2)

        return {
            "csat_delta_pct": csat_delta,
            "csat_change": round(csat_change, 4),
            "customer_clv": customer_clv,
            "monthly_active": monthly_active,
            "retention_lift": round(retention_lift, 4),
            "additional_retained_customers": additional_retained,
            "monthly_revenue_impact": monthly_revenue,
            "annual_revenue_impact": annual_revenue,
            "currency": "USD",
        }

    def escalation_to_cost(
        self, escalation_delta: float, avg_escalation_cost: float
    ) -> Dict[str, Any]:
        if avg_escalation_cost < 0:
            return {"error": "avg_escalation_cost must be non-negative"}

        escalation_change = escalation_delta / 100.0

        return {
            "escalation_delta_pct": escalation_delta,
            "escalation_change": round(escalation_change, 4),
            "avg_escalation_cost": avg_escalation_cost,
            "cost_impact_per_escalation": round(avg_escalation_cost * escalation_change, 2),
            "currency": "USD",
        }

    def calculate_business_impact(
        self, metric_deltas: Dict[str, float], business_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        total_savings = 0.0
        breakdown = {}

        resolution_delta = metric_deltas.get("resolution_delta", 0.0)
        if resolution_delta != 0:
            monthly_volume = business_params.get("monthly_volume", 0)
            cost_per_resolution = business_params.get("cost_per_resolution", 0)
            if monthly_volume > 0 and cost_per_resolution > 0:
                result = self.resolution_to_savings(
                    resolution_delta, monthly_volume, cost_per_resolution
                )
                breakdown["resolution_savings"] = result
                total_savings += result.get("annual_savings", 0)

        csat_delta = metric_deltas.get("csat_delta", 0.0)
        if csat_delta != 0:
            customer_clv = business_params.get("customer_clv", 0)
            monthly_active = business_params.get("monthly_active", 0)
            if customer_clv > 0 and monthly_active > 0:
                result = self.csat_to_revenue(
                    csat_delta, customer_clv, monthly_active
                )
                breakdown["csat_impact"] = result
                total_savings += result.get("annual_revenue_impact", 0)

        escalation_delta = metric_deltas.get("escalation_delta", 0.0)
        if escalation_delta != 0:
            avg_escalation_cost = business_params.get("avg_escalation_cost", 0)
            monthly_escalations = business_params.get("monthly_escalations", 0)
            if avg_escalation_cost > 0:
                result = self.escalation_to_cost(
                    escalation_delta, avg_escalation_cost
                )
                breakdown["escalation_impact"] = result
                if monthly_escalations > 0:
                    cost_per = result.get("cost_impact_per_escalation", 0)
                    total_savings += cost_per * monthly_escalations * 12

        return {
            "total_annual_impact": round(total_savings, 2),
            "currency": "USD",
            "breakdown": breakdown,
            "metric_deltas": metric_deltas,
        }

# history: feat: add KPIImpactCalculator with resolution savings