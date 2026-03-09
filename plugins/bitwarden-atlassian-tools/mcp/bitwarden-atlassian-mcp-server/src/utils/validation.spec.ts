import { describe, it, expect } from 'vitest';
import {
  GetIssueSchema,
  GetIssueCommentsSchema,
  SearchIssuesSchema,
  ListProjectsSchema,
  GetConfluencePageSchema,
  GetConfluencePageCommentsSchema,
  GetChildPagesSchema,
  SearchConfluenceSchema,
  SearchConfluenceCqlSchema,
  ListSpacesSchema,
  DownloadAttachmentSchema,
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

// ── Confluence Schemas ──────────────────────────────────────────────

describe('GetConfluencePageSchema', () => {
  it('should reject empty pageId', () => {
    expect(() => GetConfluencePageSchema.parse({ pageId: '' })).toThrow();
  });

  it('should accept numeric string pageId', () => {
    const result = GetConfluencePageSchema.parse({ pageId: '12345' });
    expect(result.pageId).toBe('12345');
  });

  it('should apply defaults for includeBody and bodyFormat', () => {
    const result = GetConfluencePageSchema.parse({ pageId: '1' });
    expect(result.includeBody).toBe(true);
    expect(result.bodyFormat).toBe('storage');
  });

  it('should accept all bodyFormat variants', () => {
    for (const fmt of ['storage', 'view', 'export_view']) {
      const result = GetConfluencePageSchema.parse({ pageId: '1', bodyFormat: fmt });
      expect(result.bodyFormat).toBe(fmt);
    }
  });

  it('should reject invalid bodyFormat', () => {
    expect(() =>
      GetConfluencePageSchema.parse({ pageId: '1', bodyFormat: 'invalid' })
    ).toThrow();
  });
});

describe('GetConfluencePageCommentsSchema', () => {
  it('should reject empty pageId', () => {
    expect(() => GetConfluencePageCommentsSchema.parse({ pageId: '' })).toThrow();
  });

  it('should apply defaults', () => {
    const result = GetConfluencePageCommentsSchema.parse({ pageId: '1' });
    expect(result.limit).toBe(25);
    expect(result.includeReplies).toBe(true);
    expect(result.bodyFormat).toBe('storage');
  });

  it('should reject limit over 100', () => {
    expect(() =>
      GetConfluencePageCommentsSchema.parse({ pageId: '1', limit: 101 })
    ).toThrow();
  });

  it('should reject limit less than 1', () => {
    expect(() =>
      GetConfluencePageCommentsSchema.parse({ pageId: '1', limit: 0 })
    ).toThrow();
  });

  it('should accept storage and view bodyFormat', () => {
    expect(
      GetConfluencePageCommentsSchema.parse({ pageId: '1', bodyFormat: 'storage' }).bodyFormat
    ).toBe('storage');
    expect(
      GetConfluencePageCommentsSchema.parse({ pageId: '1', bodyFormat: 'view' }).bodyFormat
    ).toBe('view');
  });

  it('should reject export_view bodyFormat', () => {
    expect(() =>
      GetConfluencePageCommentsSchema.parse({ pageId: '1', bodyFormat: 'export_view' })
    ).toThrow();
  });
});

describe('GetChildPagesSchema', () => {
  it('should reject empty pageId', () => {
    expect(() => GetChildPagesSchema.parse({ pageId: '' })).toThrow();
  });

  it('should apply default limit', () => {
    const result = GetChildPagesSchema.parse({ pageId: '1' });
    expect(result.limit).toBe(25);
  });

  it('should reject limit over 250', () => {
    expect(() =>
      GetChildPagesSchema.parse({ pageId: '1', limit: 251 })
    ).toThrow();
  });

  it('should reject limit less than 1', () => {
    expect(() =>
      GetChildPagesSchema.parse({ pageId: '1', limit: 0 })
    ).toThrow();
  });
});

describe('SearchConfluenceSchema', () => {
  it('should accept empty object', () => {
    const result = SearchConfluenceSchema.parse({});
    expect(result.limit).toBe(25);
  });

  it('should apply default limit', () => {
    const result = SearchConfluenceSchema.parse({});
    expect(result.limit).toBe(25);
  });

  it('should reject limit over 250', () => {
    expect(() => SearchConfluenceSchema.parse({ limit: 251 })).toThrow();
  });

  it('should reject limit less than 1', () => {
    expect(() => SearchConfluenceSchema.parse({ limit: 0 })).toThrow();
  });

  it('should accept optional strings', () => {
    const result = SearchConfluenceSchema.parse({ spaceKey: 'EN', title: 'Test' });
    expect(result.spaceKey).toBe('EN');
    expect(result.title).toBe('Test');
  });
});

describe('SearchConfluenceCqlSchema', () => {
  it('should reject empty cql', () => {
    expect(() => SearchConfluenceCqlSchema.parse({ cql: '' })).toThrow();
  });

  it('should accept valid cql', () => {
    const result = SearchConfluenceCqlSchema.parse({ cql: 'space = "EN"' });
    expect(result.cql).toBe('space = "EN"');
  });

  it('should apply default limit', () => {
    const result = SearchConfluenceCqlSchema.parse({ cql: 'type = page' });
    expect(result.limit).toBe(10);
  });

  it('should apply default start', () => {
    const result = SearchConfluenceCqlSchema.parse({ cql: 'type = page' });
    expect(result.start).toBe(0);
  });

  it('should reject limit over 100', () => {
    expect(() =>
      SearchConfluenceCqlSchema.parse({ cql: 'type = page', limit: 101 })
    ).toThrow();
  });

  it('should reject limit less than 1', () => {
    expect(() =>
      SearchConfluenceCqlSchema.parse({ cql: 'type = page', limit: 0 })
    ).toThrow();
  });

  it('should reject negative start', () => {
    expect(() =>
      SearchConfluenceCqlSchema.parse({ cql: 'type = page', start: -1 })
    ).toThrow();
  });
});

describe('ListSpacesSchema', () => {
  it('should apply default limit', () => {
    const result = ListSpacesSchema.parse({});
    expect(result.limit).toBe(25);
  });

  it('should reject limit over 250', () => {
    expect(() => ListSpacesSchema.parse({ limit: 251 })).toThrow();
  });

  it('should reject limit less than 1', () => {
    expect(() => ListSpacesSchema.parse({ limit: 0 })).toThrow();
  });

  it('should accept optional type', () => {
    const result = ListSpacesSchema.parse({ type: 'global' });
    expect(result.type).toBe('global');
  });

  it('should accept empty object', () => {
    const result = ListSpacesSchema.parse({});
    expect(result).toBeDefined();
  });
});

// ── DownloadAttachmentSchema (SSRF origin validation) ───────────────

describe('DownloadAttachmentSchema', () => {
  const validUrl =
    'https://mycompany.atlassian.net/secure/attachment/12345/file.pdf';

  it('should accept a valid *.atlassian.net attachment URL', () => {
    const result = DownloadAttachmentSchema.parse({ attachmentUrl: validUrl });
    expect(result.attachmentUrl).toBe(validUrl);
    expect(result.maxSizeMB).toBe(10);
  });

  it('should accept a REST API style attachment URL', () => {
    const restUrl =
      'https://mycompany.atlassian.net/rest/api/2/attachment/12345';
    const result = DownloadAttachmentSchema.parse({ attachmentUrl: restUrl });
    expect(result.attachmentUrl).toBe(restUrl);
  });

  it('should accept any *.atlassian.net subdomain', () => {
    const otherUrl =
      'https://other-company.atlassian.net/secure/attachment/12345/file.pdf';
    const result = DownloadAttachmentSchema.parse({ attachmentUrl: otherUrl });
    expect(result.attachmentUrl).toBe(otherUrl);
  });

  it('should reject a non-atlassian.net hostname (SSRF)', () => {
    expect(() =>
      DownloadAttachmentSchema.parse({
        attachmentUrl:
          'https://attacker.com/secure/attachment/123/file.pdf',
      })
    ).toThrow();
  });

  it('should reject a sibling domain attack', () => {
    expect(() =>
      DownloadAttachmentSchema.parse({
        attachmentUrl:
          'https://company.atlassian.net.evil.com/secure/attachment/123/file.pdf',
      })
    ).toThrow();
  });

  it('should reject a URL that is not a valid URL', () => {
    expect(() =>
      DownloadAttachmentSchema.parse({ attachmentUrl: 'not-a-url' })
    ).toThrow();
  });

  it('should reject a URL missing the attachment path pattern', () => {
    expect(() =>
      DownloadAttachmentSchema.parse({
        attachmentUrl: 'https://mycompany.atlassian.net/browse/PROJ-1',
      })
    ).toThrow();
  });

  it('should reject a URL with the attachment pattern only in the query string', () => {
    expect(() =>
      DownloadAttachmentSchema.parse({
        attachmentUrl:
          'https://mycompany.atlassian.net/rest/api/2/user?key=admin&x=/secure/attachment/',
      })
    ).toThrow();
  });

  it('should reject an empty string', () => {
    expect(() =>
      DownloadAttachmentSchema.parse({ attachmentUrl: '' })
    ).toThrow();
  });

  describe('maxSizeMB bounds', () => {
    it('should accept maxSizeMB of 1 (minimum)', () => {
      const result = DownloadAttachmentSchema.parse({
        attachmentUrl: validUrl,
        maxSizeMB: 1,
      });
      expect(result.maxSizeMB).toBe(1);
    });

    it('should accept maxSizeMB of 50 (maximum)', () => {
      const result = DownloadAttachmentSchema.parse({
        attachmentUrl: validUrl,
        maxSizeMB: 50,
      });
      expect(result.maxSizeMB).toBe(50);
    });

    it('should reject maxSizeMB of 0', () => {
      expect(() =>
        DownloadAttachmentSchema.parse({
          attachmentUrl: validUrl,
          maxSizeMB: 0,
        })
      ).toThrow();
    });

    it('should reject maxSizeMB over 50', () => {
      expect(() =>
        DownloadAttachmentSchema.parse({
          attachmentUrl: validUrl,
          maxSizeMB: 51,
        })
      ).toThrow();
    });

    it('should default maxSizeMB to 10', () => {
      const result = DownloadAttachmentSchema.parse({
        attachmentUrl: validUrl,
      });
      expect(result.maxSizeMB).toBe(10);
    });
  });
});
