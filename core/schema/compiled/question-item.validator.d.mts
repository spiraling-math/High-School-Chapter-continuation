// Hand-written types for the GENERATED standalone validator.
interface AjvError {
  instancePath: string;
  schemaPath: string;
  keyword: string;
  params: Record<string, unknown>;
  message?: string;
}
type ValidateFn = ((data: unknown) => boolean) & { errors?: AjvError[] | null };
declare const validate: ValidateFn;
export default validate;
export { validate };
