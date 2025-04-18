import _ from 'lodash';

export const flattenObjectProperties = (obj: any) => {
  if (!obj || obj.type !== 'object' || !obj.properties) {
    return [obj];
  }

  const result: any[] = [];

  const flatten = (item: any, parentKey = '') => {
    _.forOwn(item, (value, key) => {
      const newKey = parentKey ? `${parentKey}.${key}` : key;
      if (value.type === 'object' && value.properties) {
        flatten(value.properties, newKey);
      } else {
        result.push({ ...value, name: newKey });
      }
    });
  };

  flatten(obj.properties);
  return result;
}; 