from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ValidationIssue(BaseModel):
    """
    Represents a single validation issue found during code validation
    """
    type: str = Field(
        description="Type of issue (syntax, integration, functionality, style)"
    )
    severity: str = Field(
        description="Severity level (critical, error, warning, info)"
    )
    message: str = Field(
        description="Detailed description of the issue"
    )
    code: Optional[str] = Field(
        default=None,
        description="Code snippet where the issue was found"
    )
    line: Optional[int] = Field(
        default=None,
        description="Line number where the issue was found"
    )
    affected_segment: Optional[str] = Field(
        default=None,
        description="Segment type affected (game_ui, game_logic, game_class, css, audio)"
    )
    suggested_fix: Optional[str] = Field(
        default=None,
        description="Suggested code to fix the issue"
    )
    responsible_crew: Optional[str] = Field(
        default=None,
        description="The crew responsible for fixing this issue (engine_crew, entity_crew, level_crew, ui_crew)"
    )

class ValidationResults(BaseModel):
    """
    Represents the complete validation results for a game integration
    """
    error_count: int = Field(
        default=0,
        description="Total number of errors found"
    )
    warning_count: int = Field(
        default=0,
        description="Total number of warnings found"
    )
    issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="All issues found during validation"
    )
    engine_issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Issues specific to the engine code"
    )
    entity_issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Issues specific to the entity code"
    )
    level_issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Issues specific to the level code"
    )
    ui_issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Issues specific to the UI code"
    )
    critical_issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Critical issues that must be fixed"
    )
    improvements: List[str] = Field(
        default_factory=list,
        description="Suggested improvements that aren't errors"
    )
    
    def categorize_issues(self):
        """
        Categorize issues by crew and severity
        """
        # Reset categorized lists
        self.engine_issues = []
        self.entity_issues = []
        self.level_issues = []
        self.ui_issues = []
        self.critical_issues = []
        
        # Count errors and warnings
        self.error_count = 0
        self.warning_count = 0
        
        # Categorize each issue
        for issue in self.issues:
            # Categorize by severity
            if issue.severity == "critical":
                self.critical_issues.append(issue)
                self.error_count += 1
            elif issue.severity == "error":
                self.error_count += 1
            elif issue.severity == "warning":
                self.warning_count += 1
            
            # Categorize by crew
            if issue.responsible_crew == "engine_crew" or issue.affected_segment == "game_class":
                self.engine_issues.append(issue)
            elif issue.responsible_crew == "entity_crew":
                self.entity_issues.append(issue)
            elif issue.responsible_crew == "level_crew":
                self.level_issues.append(issue)
            elif issue.responsible_crew == "ui_crew" or issue.affected_segment in ["game_ui", "css", "audio"]:
                self.ui_issues.append(issue) 