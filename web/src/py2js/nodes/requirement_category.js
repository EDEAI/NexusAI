// Importing necessary modules and classes
import { v4 as uuidv4 } from 'uuid';
import { Prompt } from '../prompt.js';
import { VariableTypes } from '../variables.js';
import { Node } from './base.js';

/**
 * A class to manage requirement categories, each represented as an object with an ID and content.
 */
export class RequirementCategory {
    constructor() {
        /**
         * Initializes the RequirementCategory object with an empty array to store categories.
         */
        this.categories = [];
    }

    /**
     * Adds a new category to the array of categories.
     *
     * @param {string} content The content of the requirement category.
     */
    addCategory(content, id) {
        const category = {
            id: id || uuidv4(),
            content: content,
        };
        this.categories.push(category);
    }

    /**
     * Retrieves the name of the category given its ID.
     *
     * @param {string} categoryId The ID of the category to find.
     * @return {string} The content (name) of the category if found, otherwise returns an empty string.
     */
    getCategoryNameById(categoryId) {
        const category = this.categories.find(cat => cat.id === categoryId);
        return category ? category.content : '';
    }

    /**
     * Converts the array of categories to an array of objects.
     *
     * @return {Object[]} An array of objects, each representing a requirement category.
     */
    toObject() {
        return this.categories;
    }
}

/**
 * Creates an instance of RequirementCategory from an array of objects.
 *
 * @param {Object[]} categoriesList An array of objects, each representing a requirement category.
 * @return {RequirementCategory} An instance of RequirementCategory populated with the provided categories.
 */
export function createRequirementCategoryFromObject(categoriesList) {
    const requirementCategory = new RequirementCategory();
    requirementCategory.categories = categoriesList;
    return requirementCategory;
}

/**
 * A RequirementCategoryNode object is used to create requirement categories in a workflow.
 * Inherits from the Node class.
 */
export class RequirementCategoryNode extends Node {
    /**
 * Initialize a RequirementCategoryNode object with specific attribute requirements.
 * The backend output defaults to a string type Variable named 'category_name'.
 *
 * @param {Object} params - An object containing initialization parameters.
 * @param {string} params.title - The title of the node.
 * @param {string} [params.desc=""] - The description of the node.
 * @param {VariableTypes|null} [params.input=null] - The input variables for the node.
 * @param {number} [params.model_config_id=0] - The model configuration ID.
 * @param {RequirementCategory|null} [params.requirement_category=null] - The requirement category associated with the node.
 * @param {Prompt|null} [params.prompt=null] - The prompt associated with the node.
 * @param {boolean} [params.manual_confirmation=false] - Whether manual confirmation is required.
 * @param {Object} [params.position={}] - The position of the node.
 * @param {number} [params.width=0] - The width of the node.
 * @param {number} [params.height=0] - The height of the node.
 * @param {boolean} [params.selected=false] - Whether the node is selected.
 * @param {string|null} [params.original_node_id=null] - The original node ID, if any.
 */
    constructor({
        title,
        desc = '',
        input = null,
        model_config_id = 0,
        requirement_category = null,
        prompt = null,
        manual_confirmation = false,
        position = {},
        flow_data = {},
        width = 0,
        height = 0,
        selected = false,
        original_node_id = null,
    }) {
        // Constructing the initialization object
        const initKwargs = {
            type: 'requirement_category',
            title,
            desc,
            input,
            model_config_id,
            requirement_category,
            prompt,

            flow_data,
        };

        // Adding the original node ID if provided
        if (original_node_id !== null) {
            initKwargs.original_node_id = original_node_id;
        }

        // Calling the parent class constructor
        super(initKwargs);
    }
}

// Exporting the RequirementCategoryNode class for use in other modules
