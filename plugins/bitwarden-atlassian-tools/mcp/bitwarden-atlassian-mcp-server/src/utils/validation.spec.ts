import { describe, it, expect } from 'vitest';
import {
  GetIssueSchema,
  GetIssueCommentsSchema,
  SearchIssuesSchema,
  ListProjectsSchema,
  validateInput,
} from './validation.js';

describe('GetIssueSchema', () => {
  describe('issueIdOrKey validation', () => {
    it.each([
      ['PROJ-123', 'standard key'],
      ['AB-1', 'short project key'],
      ['A_B-99', 'key with underscore'],
      ['ABC123-456', 'alphanumeric project key'],
      ['12345', 'numeric ID'],
      ['1', 'single digit ID'],
    ])('should accept valid input: %s (%s)', (input) => {
      const result = GetIssueSchema.parse({ issueIdOrKey: input });
      expect(result.issueIdOrKey).toBe(input);
    });

    it.each([
      ['../../admin', 'path traversal'],
      ['PROJ-1/../../evil', 'path traversal with key prefix'],
      ['', 'empty string'],
      ['proj-123', 'lowercase project key'],
      ['PROJ-', 'missing number'],
      ['-123', 'missing project key'],
      ['PROJ', 'missing dash and number'],
      ['PROJ-abc', 'non-numeric after dash'],
      ['PROJ-123 ', 'trailing space'],
      [' PROJ-123', 'leading space'],
      ['PROJ-123\n', 'newline'],
      ['PROJ-0123abc', 'trailing alpha after number'],
    ])('should reject invalid input: %s (%s)', (input) => {
      expect(() => GetIssueSchema.parse({ issueIdOrKey: input })).toThrow();
    });
  });

  it('should allow optional fields and expand', () => {
    const result = GetIssueSchema.parse({
      issueIdOrKey: 'PROJ-1',
      fields: ['summary', 'status'],
      expand: ['changelog'],
    });
    expect(result.fields).toEqual(['summary', 'status']);
    expect(result.expand).toEqual(['changelog']);
  });
});

describe('GetIssueCommentsSchema', () => {
  it('should validate issueIdOrKey with same regex', () => {
    expect(() =>
      GetIssueCommentsSchema.parse({ issueIdOrKey: '../../etc/passwd' })
    ).toThrow();
  });

  it('should apply defaults for startAt and maxResults', () => {
    const result = GetIssueCommentsSchema.parse({ issueIdOrKey: 'PROJ-1' });
    expect(result.startAt).toBe(0);
    expect(result.maxResults).toBe(50);
  });

  it('should reject maxResults over 100', () => {
    expect(() =>
      GetIssueCommentsSchema.parse({ issueIdOrKey: 'PROJ-1', maxResults: 101 })
    ).toThrow();
  });

  it('should reject negative startAt', () => {
    expect(() =>
      GetIssueCommentsSchema.parse({ issueIdOrKey: 'PROJ-1', startAt: -1 })
    ).toThrow();
  });
});

describe('SearchIssuesSchema', () => {
  it('should require non-empty jql', () => {
    expect(() => SearchIssuesSchema.parse({ jql: '' })).toThrow();
  });

  it('should apply default maxResults', () => {
    const result = SearchIssuesSchema.parse({ jql: 'project = TEST' });
    expect(result.maxResults).toBe(50);
  });

  it('should accept nextPageToken', () => {
    const result = SearchIssuesSchema.parse({
      jql: 'project = TEST',
      nextPageToken: 'abc123',
    });
    expect(result.nextPageToken).toBe('abc123');
  });
});

describe('ListProjectsSchema', () => {
  it('should apply default maxResults', () => {
    const result = ListProjectsSchema.parse({});
    expect(result.maxResults).toBe(50);
  });

  it('should reject maxResults over 100', () => {
    expect(() => ListProjectsSchema.parse({ maxResults: 200 })).toThrow();
  });
});

describe('validateInput', () => {
  it('should return validated data for valid input', () => {
    const result = validateInput(GetIssueSchema, { issueIdOrKey: 'PROJ-1' });
    expect(result.issueIdOrKey).toBe('PROJ-1');
  });

  it('should throw formatted error for invalid input', () => {
    expect(() => validateInput(GetIssueSchema, { issueIdOrKey: '' })).toThrow(
      /Validation failed/
    );
  });

  it('should include field path in error message', () => {
    expect.assertions(1);
    try {
      validateInput(GetIssueSchema, { issueIdOrKey: 'bad' });
    } catch (e: any) {
      expect(e.message).toContain('issueIdOrKey');
    }
  });
});
