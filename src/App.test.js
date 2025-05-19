import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Asset Management header', () => {
  render(<App />);
  const headerElement = screen.getByText(/Asset Management/i);
  expect(headerElement).toBeInTheDocument();
});

test('renders dashboard by default', () => {
  render(<App />);
  const portfolioElement = screen.getByText(/Portfolio Performance/i);
  expect(portfolioElement).toBeInTheDocument();
});
