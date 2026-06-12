import './Skeleton.css';

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'rect' | 'circle';
  className?: string;
}

export function Skeleton({ width = '100%', height = '1rem', variant = 'rect', className = '' }: SkeletonProps) {
  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height,
  };

  return <div className={`skeleton skeleton-${variant} ${className}`} style={style} aria-hidden="true" />;
}

export function SessionCardSkeleton() {
  return (
    <div className="session-card skeleton-card">
      <div className="session-header">
        <Skeleton width={120} height={20} />
        <Skeleton width={80} height={24} variant="rect" />
      </div>
      <div className="session-details">
        <Skeleton width="60%" height={14} />
        <Skeleton width="40%" height={14} />
      </div>
      <div className="session-meta">
        <Skeleton width={100} height={12} />
        <Skeleton width={80} height={12} />
      </div>
      <div className="session-actions">
        <Skeleton width={60} height={32} variant="rect" />
        <Skeleton width={60} height={32} variant="rect" />
        <Skeleton width={60} height={32} variant="rect" />
      </div>
    </div>
  );
}

export function TableRowSkeleton({ columns = 5 }: { columns?: number }) {
  return (
    <tr className="skeleton-row">
      {Array.from({ length: columns }).map((_, i) => (
        <td key={i}>
          <Skeleton width={`${60 + Math.random() * 40}%`} height={16} />
        </td>
      ))}
    </tr>
  );
}
