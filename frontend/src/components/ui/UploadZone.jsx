import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, CheckCircle, CloudUpload } from 'lucide-react'
import { colors } from '../../theme/colors'

export default function UploadZone({ uploadState, fileInfo, onUpload }) {
  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0])
      }
    },
    [onUpload]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
    disabled: uploadState === 'processing',
  })

  // Loaded state — show file info card
  if (uploadState === 'ready' && fileInfo) {
    return (
      <div
        className="fade-in-up"
        style={{
          padding: '16px',
          backgroundColor: '#FFFFFF',
          border: `1px solid ${colors.border}`,
          borderRadius: '12px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #FEE2E2, #FECACA)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <FileText size={22} color="#DC2626" />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontSize: '13px',
                fontWeight: 600,
                color: colors.textPrimary,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {fileInfo.fileName}
            </div>
            <div
              style={{
                fontSize: '12px',
                color: '#94A3B8',
                marginTop: '3px',
              }}
            >
              {fileInfo.pages} pages · {fileInfo.chunks?.toLocaleString()} chunks
            </div>
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '5px',
              fontSize: '11px',
              fontWeight: 600,
              color: '#059669',
              backgroundColor: '#D1FAE5',
              padding: '4px 10px',
              borderRadius: '50px',
              flexShrink: 0,
            }}
          >
            <CheckCircle size={12} />
            Ready
          </div>
        </div>
      </div>
    )
  }

  // Processing state
  if (uploadState === 'processing') {
    return (
      <div
        style={{
          padding: '28px 20px',
          background: 'linear-gradient(135deg, #EEF2FF, #E0E7FF)',
          border: `2px solid #A5B4FC`,
          borderRadius: '12px',
          textAlign: 'center',
        }}
      >
        <div className="spinner" style={{ margin: '0 auto 14px' }} />
        <div
          style={{
            fontSize: '13px',
            fontWeight: 600,
            color: '#4338CA',
          }}
        >
          Indexing PDF...
        </div>
        <div
          style={{
            fontSize: '12px',
            color: '#6366F1',
            marginTop: '6px',
            opacity: 0.7,
          }}
        >
          Chunking and embedding document
        </div>
        {/* Progress bar */}
        <div
          style={{
            marginTop: '14px',
            height: '4px',
            borderRadius: '2px',
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
            overflow: 'hidden',
          }}
        >
          <div
            className="bar-animate"
            style={{
              width: '70%',
              height: '100%',
              borderRadius: '2px',
              background: 'linear-gradient(90deg, #6366F1, #818CF8)',
            }}
          />
        </div>
      </div>
    )
  }

  // Empty / drag state
  return (
    <div
      {...getRootProps()}
      className={isDragActive ? 'upload-dragging' : ''}
      style={{
        padding: '28px 20px',
        background: isDragActive
          ? 'linear-gradient(135deg, #DBEAFE, #BFDBFE)'
          : 'linear-gradient(135deg, #F0F7FF, #E6F1FB)',
        border: `2px dashed ${isDragActive ? '#2563EB' : '#93C5FD'}`,
        borderRadius: '12px',
        textAlign: 'center',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
      }}
      onMouseEnter={(e) => {
        if (!isDragActive) {
          e.currentTarget.style.borderColor = '#60A5FA'
          e.currentTarget.style.background = 'linear-gradient(135deg, #DBEAFE, #E6F1FB)'
        }
      }}
      onMouseLeave={(e) => {
        if (!isDragActive) {
          e.currentTarget.style.borderColor = '#93C5FD'
          e.currentTarget.style.background = 'linear-gradient(135deg, #F0F7FF, #E6F1FB)'
        }
      }}
    >
      <input {...getInputProps()} />
      <div
        style={{
          width: '48px',
          height: '48px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #3B82F6, #2563EB)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 12px',
          boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
        }}
      >
        <CloudUpload size={22} color="#FFFFFF" />
      </div>
      <div
        style={{
          fontSize: '14px',
          fontWeight: 600,
          color: '#1E40AF',
        }}
      >
        {isDragActive ? 'Drop PDF here' : 'Upload Annual Report'}
      </div>
      <div
        style={{
          fontSize: '12px',
          color: '#64748B',
          marginTop: '6px',
        }}
      >
        PDF · 10-K · Earnings · up to 50MB
      </div>
    </div>
  )
}
