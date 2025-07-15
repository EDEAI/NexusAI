# VariableInput Component

A universal input component that automatically detects variable types and renders appropriate input components with built-in validation. This component follows the same patterns as the existing `RenderInput` component in the workflow system.

## Features

- 🔄 **Auto Type Detection**: Automatically renders the correct input component based on variable type
- ✅ **Built-in Validation**: Comprehensive validation rules for each data type
- 🌐 **Internationalization**: Full i18n support with existing locale keys
- 🎨 **Consistent UI**: Uses ProForm components for consistency with the rest of the application
- 📝 **Type Safety**: Full TypeScript support with comprehensive type definitions

## Supported Variable Types

| Type | Component | Description |
|------|-----------|-------------|
| `string` | ProFormTextArea | Text input with optional length validation |
| `number` | ProFormDigit | Numeric input with precision support |
| `file` | UploadDragger | File upload with drag & drop support |
| `json` | ProFormTextArea | JSON input with format validation |

## Basic Usage

```tsx
import VariableInput from '@/components/common/VariableInput';

// String variable
<VariableInput
  variable={{
    name: 'user_name',
    type: 'string',
    display_name: 'User Name',
    required: true,
    max_length: 50
  }}
  onChange={(value) => console.log(value)}
/>

// Number variable
<VariableInput
  variable={{
    name: 'age',
    type: 'number',
    display_name: 'Age',
    required: true
  }}
  onChange={(value) => console.log(value)}
/>

// File variable
<VariableInput
  variable={{
    name: 'document',
    type: 'file',
    display_name: 'Upload Document',
    required: false
  }}
  fileConfig={{
    accept: '.pdf,.doc,.docx',
    maxSize: 10,
    multiple: false
  }}
/>

// JSON variable
<VariableInput
  variable={{
    name: 'config',
    type: 'json',
    display_name: 'Configuration',
    value: { key: 'value' }
  }}
  onChange={(value) => console.log(JSON.parse(value))}
/>
```

## Batch Rendering

For rendering multiple variables (similar to RenderInput):

```tsx
import VariableInput from '@/components/common/VariableInput';

const MultipleVariables = ({ variables }) => {
  return (
    <div>
      {Object.values(variables)
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((variable) => (
          <VariableInput
            key={variable.name}
            variable={variable}
            onChange={(value) => handleVariableChange(variable.name, value)}
          />
        ))}
    </div>
  );
};
```

## API Reference

### VariableInputProps

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `variable` | `Variable` | ✅ | - | Variable configuration object |
| `disabled` | `boolean` | ❌ | `false` | Whether the input is disabled |
| `readonly` | `boolean` | ❌ | `false` | Whether the input is read-only |
| `onChange` | `(value: any) => void` | ❌ | - | Callback when value changes |
| `onValidationChange` | `(isValid: boolean) => void` | ❌ | - | Callback when validation status changes |
| `fileConfig` | `FileConfig` | ❌ | - | File-specific configuration |
| `className` | `string` | ❌ | - | Custom CSS class |
| `style` | `React.CSSProperties` | ❌ | - | Custom inline styles |

### Variable

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `name` | `string` | ✅ | - | Variable name (used as form field name) |
| `type` | `VariableType` | ✅ | - | Variable type (`'string' \| 'number' \| 'file' \| 'json'`) |
| `value` | `any` | ❌ | - | Initial/default value |
| `display_name` | `string` | ❌ | - | Display label (falls back to name) |
| `required` | `boolean` | ❌ | `false` | Whether the field is required |
| `max_length` | `number` | ❌ | - | Maximum length (for string type) |
| `sort_order` | `number` | ❌ | `0` | Sort order for rendering |

### FileConfig

| Property | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `accept` | `string` | ❌ | `'.txt,.md,.pdf,.html,.xlsx,.pptx,.docx,.csv,.jpg,.png,.jpeg'` | Accepted file types |
| `maxSize` | `number` | ❌ | `15` | Maximum file size in MB |
| `multiple` | `boolean` | ❌ | `false` | Allow multiple file selection |

## Validation

The component includes built-in validation for each type:

### String Validation
- Required field validation
- Maximum length validation (if `max_length` is specified)

### Number Validation
- Required field validation
- Numeric format validation (handled by ProFormDigit)

### File Validation
- Required field validation
- File type validation (based on `accept` pattern)
- File size validation (based on `maxSize`)

### JSON Validation
- Required field validation
- JSON format validation (validates parsing)

## Integration with Forms

The component is designed to work seamlessly with ProForm:

```tsx
import { ProForm } from '@ant-design/pro-components';
import VariableInput from '@/components/common/VariableInput';

<ProForm onFinish={handleSubmit}>
  <VariableInput
    variable={{
      name: 'user_input',
      type: 'string',
      display_name: 'User Input',
      required: true
    }}
  />
  {/* Other form fields */}
</ProForm>
```

## Migration from RenderInput

If you're migrating from the existing `RenderInput` component:

```tsx
// Old RenderInput usage
<RenderInput data={inputsData} />

// New VariableInput usage
{Object.values(inputsData).map((variable) => (
  <VariableInput key={variable.name} variable={variable} />
))}
```

## Extending with New Types

To add support for new variable types:

1. Create a new handler component in `handlers/`
2. Add the type to `VariableType` in `types.ts`
3. Update the switch statement in `useTypeDetection.ts`
4. Add validation rules in `utils/validation.ts`

## Examples

### Complete Form Example

```tsx
import React, { useState } from 'react';
import { ProForm, ProFormSubmitter } from '@ant-design/pro-components';
import VariableInput from '@/components/common/VariableInput';

const DynamicForm = () => {
  const [variables] = useState([
    {
      name: 'title',
      type: 'string',
      display_name: 'Title',
      required: true,
      max_length: 100,
      sort_order: 1
    },
    {
      name: 'price',
      type: 'number',
      display_name: 'Price',
      required: true,
      sort_order: 2
    },
    {
      name: 'image',
      type: 'file',
      display_name: 'Product Image',
      required: false,
      sort_order: 3
    },
    {
      name: 'metadata',
      type: 'json',
      display_name: 'Metadata',
      value: { category: 'electronics' },
      sort_order: 4
    }
  ]);

  const handleSubmit = (values) => {
    console.log('Form values:', values);
  };

  return (
    <ProForm onFinish={handleSubmit}>
      {variables
        .sort((a, b) => a.sort_order - b.sort_order)
        .map((variable) => (
          <VariableInput
            key={variable.name}
            variable={variable}
            fileConfig={{
              accept: '.jpg,.png,.gif',
              maxSize: 5,
              multiple: false
            }}
          />
        ))}
      <ProFormSubmitter />
    </ProForm>
  );
};
```

## Browser Support

This component supports all modern browsers and follows the same compatibility requirements as the rest of the application.

## Contributing

When contributing to this component:

1. Follow the existing code style and patterns
2. Add appropriate TypeScript types
3. Include unit tests for new functionality
4. Update this README for any API changes
5. Ensure internationalization keys are properly defined 