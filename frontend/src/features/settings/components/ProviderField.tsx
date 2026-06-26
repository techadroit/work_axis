import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  IconButton,
  Link,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  ContentCopy,
} from '@mui/icons-material';
import type { ProviderField as ProviderFieldType } from '../types';

interface ProviderFieldProps {
  field: ProviderFieldType;
  fieldKey: string;
  fieldValue: string;
  isPasswordVisible: boolean;
  onToggleVisibility: (fieldKey: string) => void;
  onCopyToClipboard: (value: string) => void;
  onFieldChange: (fieldKey: string, value: string) => void;
}

/**
 * ProviderField - Renders a single field for a model provider
 */
export const ProviderField = ({
  field,
  fieldKey,
  fieldValue,
  isPasswordVisible,
  onToggleVisibility,
  onCopyToClipboard,
  onFieldChange,
}: ProviderFieldProps) => {
  const isPassword = field.type === 'password';

  const renderFieldDescription = (description?: string) => {
    if (!description) return null;

    // Parse HTML description and extract links
    const linkRegex = /<a href='([^']+)'[^>]*>([^<]+)<\/a>/g;
    const parts: (string | JSX.Element)[] = [];
    let lastIndex = 0;
    let match;

    while ((match = linkRegex.exec(description)) !== null) {
      // Add text before the link
      if (match.index > lastIndex) {
        parts.push(description.substring(lastIndex, match.index));
      }

      // Add the link
      parts.push(
        <Link
          key={match.index}
          href={match[1]}
          target="_blank"
          rel="noopener noreferrer"
          sx={{ color: 'primary.main', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
        >
          {match[2]}
        </Link>
      );

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < description.length) {
      parts.push(description.substring(lastIndex));
    }

    return (
      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, fontSize: '0.875rem' }}>
        {parts.length > 0 ? parts : description}
      </Typography>
    );
  };

  return (
    <Box key={field.name} sx={{ mb: 3 }}>
      <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 500 }}>
        {field.label}
        {field.required && (
          <Typography component="span" color="error.main" sx={{ ml: 0.5 }}>
            *
          </Typography>
        )}
      </Typography>

      {renderFieldDescription(field.description)}

      <TextField
        fullWidth
        type={isPassword && !isPasswordVisible ? 'password' : 'text'}
        placeholder={field.placeholder}
        required={field.required}
        value={fieldValue}
        onChange={(e) => onFieldChange(fieldKey, e.target.value)}
        sx={{
          mt: 1.5,
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'background.paper',
            '&:hover': {
              backgroundColor: 'action.hover',
            },
          },
        }}
        slotProps={{
          input: {
            endAdornment: (
              <InputAdornment position="end">
                {isPassword && (
                  <IconButton
                    onClick={() => onToggleVisibility(fieldKey)}
                    edge="end"
                    size="small"
                    sx={{ mr: 0.5 }}
                  >
                    {isPasswordVisible ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                )}
                <IconButton
                  onClick={() => onCopyToClipboard(fieldValue)}
                  edge="end"
                  size="small"
                  disabled={!fieldValue}
                >
                  <ContentCopy fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          },
        }}
      />
    </Box>
  );
};

