import type { SvgIconProps } from '@mui/material';
import {
  InsertDriveFile as FileIcon,
  PictureAsPdf as PdfIcon,
  Description as WordIcon,
  TableChart as ExcelIcon,
  Slideshow as PptIcon,
} from '@mui/icons-material';

interface FileTypeIconProps {
  fileName?: string;
  fileType?: string;
  size?: 'small' | 'medium' | 'large';
  sx?: SvgIconProps['sx'];
}

const SIZE_MAP = {
  small: 40,
  medium: 80,
  large: 120,
};

/**
 * FileTypeIcon - Returns the appropriate icon component based on file type/name
 */
export const FileTypeIcon = ({ fileName, fileType, size = 'medium', sx }: FileTypeIconProps) => {
  const iconSize = SIZE_MAP[size];
  const getFileIcon = () => {
    // Get file extension from fileName or use fileType
    const extension = fileName
      ? fileName.split('.').pop()?.toLowerCase()
      : fileType?.toLowerCase();

    switch (extension) {
      case 'pdf':
        return <PdfIcon sx={{ color: '#D32F2F', fontSize: iconSize, ...sx }} />; // Red for PDF

      case 'doc':
      case 'docx':
        return <WordIcon sx={{ color: '#2B579A', fontSize: iconSize, ...sx }} />; // Blue for Word

      case 'xls':
      case 'xlsx':
        return <ExcelIcon sx={{ color: '#217346', fontSize: iconSize, ...sx }} />; // Green for Excel

      case 'csv':
        return <ExcelIcon sx={{ color: '#217346', fontSize: iconSize, ...sx }} />; // Green for CSV

      case 'ppt':
      case 'pptx':
        return <PptIcon sx={{ color: '#D24726', fontSize: iconSize, ...sx }} />; // Orange/Red for PowerPoint

      default:
        return <FileIcon sx={{ color: '#757575', fontSize: iconSize, ...sx }} />; // Gray for generic files
    }
  };

  return getFileIcon();
};

