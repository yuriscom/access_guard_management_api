from pydantic import BaseModel, Field

class PoliciesParams(BaseModel):
    user_id: int = Field(..., description="User ID to fetch policies for")
    scope: str = Field(default="SMC", description="Scope of the policies")
    app_id: int | None = Field(default=None, description="Optional application ID to filter policies") 