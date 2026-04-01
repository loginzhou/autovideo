const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const ajv = new Ajv();

const CONFIG_ROOT = path.resolve(__dirname, '../../../../config/');

async function main(input) {
  const { payload, schema_path, max_retries = 3, retry_count = 0 } = input;
  const schemaFullPath = path.join(CONFIG_ROOT, schema_path);
  const schema = JSON.parse(fs.readFileSync(schemaFullPath, 'utf8'));
  
  const validate = ajv.compile(schema);
  const valid = validate(payload);
  
  return {
    valid: valid,
    errors: valid ? [] : validate.errors.map(e => `${e.instancePath} ${e.message}`),
    retry_allowed: retry_count < max_retries,
    retry_count: retry_count
  };
}

if (require.main === module) {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  main(input).then(result => {
    console.log(JSON.stringify(result, null, 2));
    process.exit(0);
  }).catch(err => {
    console.error(JSON.stringify({error: err.message}, null, 2));
    process.exit(1);
  });
}

module.exports = main;
