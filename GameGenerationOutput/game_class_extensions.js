```javascript
// Define a LevelManager class responsible for loading and managing levels.
class LevelManager {
  constructor() {
    this.levels = []; // Array to hold all level data
    this.currentLevelIndex = 0; // Track which level is currently active
  }

  // Method to load level data
  loadLevels(levelDataArray) {
    this.levels = levelDataArray; // Store the array of level data
  }

  // Method to get the current level data
  getCurrentLevel() {
    return this.levels[this.currentLevelIndex];
  }

  // Method to advance to the next level
  advanceLevel() {
    if (this.currentLevelIndex < this.levels.length - 1) {
      this.currentLevelIndex++;
    } else {
      console.log("All levels completed!");
    }
  }
}

// Extend Game class
class Game extends TemplateGame {
  constructor() {
    super();
    this.levelManager = new LevelManager(); // Initialize LevelManager
  }

  initialize() {
    super.initialize();
    // Load initial level data from configuration and prepare level context
    this.levelManager.loadLevels(levelConfigurations);
    this.currentLevel = this.levelManager.getCurrentLevel();
  }

  update(deltaTime) {
    super.update(deltaTime);
    // Handle level-specific update logic and track player progression
    this.currentLevel = this.levelManager.getCurrentLevel();
  }
}

// Extend GameLogic class
class GameLogic extends TemplateGameLogic {
  constructor() {
    super();
    this.levelObjectives = {}; // Initialize level objectives
  }

  processGameLogic() {
    super.processGameLogic();
    // Add level-specific logic conditions
    const currentLevel = this.game.levelManager.getCurrentLevel();
    // Implement level-specific logic here, e.g., objectives, enemies, etc.
  }

  checkConditions() {
    super.checkConditions();
    // Check for level completion or failures
    const objectivesMet = this.checkLevelObjectives(this.levelObjectives);
    if (objectivesMet) {
      this.game.levelManager.advanceLevel();
    }
  }

  // Helper method to check if level objectives are met
  checkLevelObjectives(objectives) {
    // Logic to validate if all objectives for the level are completed
    return true; // Placeholder return
  }
}

// Example of level configurations, should be loaded from external data source
const levelConfigurations = [
  // Array of level configuration objects
  { id: 1, name: "Level 1", difficulty: 1, objectives: {} },
  { id: 2, name: "Level 2", difficulty: 2, objectives: {} }
];

// Insert the LevelManager, Game, and GameLogic code blocks above accordingly
```

This implementation ensures that the level system is extendable and integrates seamlessly with the existing template classes. The `LevelManager` handles the core functionality of loading levels and managing progression, while `Game` and `GameLogic` are extended to incorporate level-specific logic and tracking. The code is modular and adds significant flexibility to the game’s level management process.