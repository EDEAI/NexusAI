/**
 * A class to represent a single category with potential subcategories.
 */
class RecursiveTaskCategory {
    /**
     * Initializes a RecursiveTaskCategory object.
     *
     * @param {string} id - The unique identifier of the category.
     * @param {string} name - The name of the category.
     * @param {string} [description=""] - The description of the category.
     * @param {string} [task=null] - The task associated with the category.
     */
    constructor(id, name, description = '', task = null) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.task = task;
        this.subcategories = [];
    }

    /**
     * Adds a subcategory to the current category.
     *
     * @param {RecursiveTaskCategory} subcategory - The subcategory to add.
     */
    addSubcategory(subcategory) {
        this.subcategories.push(subcategory);
    }

    /**
     * Converts the category to a plain object.
     *
     * @returns {Object} An object representing the category.
     */
    toObject() {
        return {
            id: this.id,
            name: this.name,
            description: this.description,
            task: this.task,
            subcategories: this.subcategories.map(sub => sub.toObject()),
        };
    }
}

/**
 * Create a RecursiveTaskCategory object from an object.
 *
 * @param {Object} categoryObject - An object representing a recursive task category.
 * @returns {RecursiveTaskCategory} An instance of RecursiveTaskCategory populated with the provided data.
 */
function createRecursiveTaskCategoryFromObject(categoryObject) {
    const category = new RecursiveTaskCategory(
        categoryObject.id,
        categoryObject.name,
        categoryObject.description,
        categoryObject.task,
    );
    for (const subcategoryObject of categoryObject.subcategories || []) {
        const subcategory = createRecursiveTaskCategoryFromObject(subcategoryObject);
        category.addSubcategory(subcategory);
    }
    return category;
}

export { RecursiveTaskCategory, createRecursiveTaskCategoryFromObject };
