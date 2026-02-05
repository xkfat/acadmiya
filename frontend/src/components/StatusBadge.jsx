import { CheckCircle2, Clock, XCircle, AlertCircle } from 'lucide-react';

const StatusBadge = ({ status }) => {
  // Define styles based on status
  const styles = {
    VALIDATED: {
      bg: 'bg-green-100',
      text: 'text-green-700',
      border: 'border-green-200',
      icon: CheckCircle2,
      label: 'Validé'
    },
    PENDING: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-700',
      border: 'border-yellow-200',
      icon: Clock,
      label: 'En Attente'
    },
    REJECTED: {
      bg: 'bg-red-100',
      text: 'text-red-700',
      border: 'border-red-200',
      icon: XCircle,
      label: 'Rejeté'
    },
    default: {
      bg: 'bg-gray-100',
      text: 'text-gray-700',
      border: 'border-gray-200',
      icon: AlertCircle,
      label: status
    }
  };

  const config = styles[status] || styles.default;
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${config.bg} ${config.text} ${config.border}`}>
      <Icon size={14} />
      {config.label}
    </span>
  );
};

export default StatusBadge;