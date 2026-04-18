import { render, screen, fireEvent } from '@testing-library/react';
import ActionBar from '../components/ActionBar';

describe('ActionBar', () => {
  const mockOnAction = vi.fn();

  beforeEach(() => {
    mockOnAction.mockClear();
  });

  it('renders all four action buttons', () => {
    render(<ActionBar disabled={false} onAction={mockOnAction} canFlee={true} />);

    expect(screen.getByText('ATTACK')).toBeInTheDocument();
    expect(screen.getByText('SPELL')).toBeInTheDocument();
    expect(screen.getByText('ITEM')).toBeInTheDocument();
    expect(screen.getByText('FLEE')).toBeInTheDocument();
  });

  it('calls onAction with "attack" when attack button is clicked', () => {
    render(<ActionBar disabled={false} onAction={mockOnAction} canFlee={true} />);

    fireEvent.click(screen.getByText('ATTACK'));

    expect(mockOnAction).toHaveBeenCalledWith('attack');
  });

  it('calls onAction with "flee" when flee button is clicked', () => {
    render(<ActionBar disabled={false} onAction={mockOnAction} canFlee={true} />);

    fireEvent.click(screen.getByText('FLEE'));

    expect(mockOnAction).toHaveBeenCalledWith('flee');
  });

  it('disables all buttons when disabled prop is true', () => {
    render(<ActionBar disabled={true} onAction={mockOnAction} canFlee={true} />);

    const buttons = screen.getAllByRole('button');
    buttons.forEach(button => {
      expect(button).toBeDisabled();
    });
  });

  it('disables flee button when canFlee is false', () => {
    render(<ActionBar disabled={false} onAction={mockOnAction} canFlee={false} />);

    expect(screen.getByRole('button', { name: /flee/i })).toBeDisabled();
  });

  it('enables flee button when canFlee is true', () => {
    render(<ActionBar disabled={false} onAction={mockOnAction} canFlee={true} />);

    expect(screen.getByRole('button', { name: /flee/i })).toBeEnabled();
  });
});
