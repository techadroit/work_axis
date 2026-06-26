export const FILE_TYPES = [
    // 'image/*',
    '.pdf',
    '.doc',
    '.docx',
    '.txt',
    '.ppt',
    '.pptx',
    '.xls',
    '.xlsx',
] as const;

export const ACCEPTED_FILE_TYPES = FILE_TYPES.join(',');
