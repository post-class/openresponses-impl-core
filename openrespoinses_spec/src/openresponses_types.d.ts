/**
 * Type-check-only facade for OpenResponses schema types.
 * This file is declaration-only and has no runtime behavior.
 */

import type { components, operations, paths } from './openresponses_models';

export type OpenResponsesPaths = paths;
export type OpenResponsesOperations = operations;
export type OpenResponsesSchemas = components['schemas'];

export type CreateResponseBody = components['schemas']['CreateResponseBody'];
export type ResponseResource = components['schemas']['ResponseResource'];
export type ResponseStreamEvent =
  operations['createResponse']['responses'][200]['content']['text/event-stream'];

export type ItemParam = components['schemas']['ItemParam'];
export type ToolChoiceParam = components['schemas']['ToolChoiceParam'];
