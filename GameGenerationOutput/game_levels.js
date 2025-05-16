```javascript
/*!
 * game_levels.js - Standalone Level System
 * This file includes all the necessary level system code and provides
 * backward compatibility for use in HTML5 games. This is a standalone script
 * that can be directly included in HTML pages if needed.
 * 
 * Description:
 * The `LevelManager` class manages level data and progression. The `Game` and
 * `GameLogic` classes are extended to support level-specific logic and tracking.
 * 
 * Usage:
 * To use this script independently, make sure the `TemplateGame` and 
 * `TemplateGameLogic` (or their equivalents) are accessible in the global 
 * scope before this file is included.
 * 
 * This file is primarily for reference and backwards compatibility with older 
 * implementations. The recommended usage is through template integration.
 */

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

// Check if TemplateGame is defined in the context
if (typeof TemplateGame !== 'undefined') {
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
}

// Check if TemplateGameLogic is defined in the context
if (typeof TemplateGameLogic !== 'undefined') {
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
}

// Example of level configurations, should be loaded from external data source
const levelConfigurations = [
  // Array of level configuration objects
  { id: 1, name: "Level 1", difficulty: 1, objectives: {} },
  { id: 2, name: "Level 2", difficulty: 2, objectives: {} }
];

/**
 * Documentation:
 * This standalone level system code was derived from extending base template
 * classes and can function independently if included on a webpage. It provides
 * a backward-compatible solution for older implementations. However, the
 * recommended approach remains integrating these functionalities within a larger
 * game architecture using template extensions for more flexibility and modularity.
 */
```