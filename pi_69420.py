#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pi 69420 Benchmark - Performance Tester

A high-performance benchmark tool that searches for multiple occurrences of the pattern
"69420" within the decimal digits of Pi. This tool measures and reports detailed
performance metrics including calculation speed, search efficiency, and discovery rates.

Features:
- High-precision Pi calculation using mpmath library
- Sliding window pattern matching algorithm
- Real-time progress monitoring with colored output
- Two operation modes: target-based and time-based
- Cross-platform emoji and color support
- Comprehensive performance metrics

Author: Pi 69420 Benchmark Team
Version: 1.0
License: MIT
"""

import time
import sys
import argparse
from collections import deque
from typing import Dict, List, Optional, Any, Tuple

# Configure colorama for cross-platform support
def setup_colorama() -> bool:
    """
    Configure colorama for cross-platform color support.

    Automatically installs colorama if not present and initializes it with
    auto-reset functionality to ensure colors don't bleed between outputs.

    Returns:
        bool: True if colorama was successfully configured

    Raises:
        subprocess.CalledProcessError: If colorama installation fails
    """
    try:
        from colorama import init, Fore, Back, Style
        init(autoreset=True)  # Auto-reset colors after each print
        return True
    except ImportError:
        print("Installing colorama for cross-platform support...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
        from colorama import init
        init(autoreset=True)
        return True

def supports_emoji() -> bool:
    """
    Detect if the current terminal supports Unicode emoji characters.

    Tests emoji support by attempting to print a test emoji and catching
    any UnicodeEncodeError that would indicate lack of emoji support.

    Returns:
        bool: True if terminal supports emojis, False otherwise
    """
    try:
        print("🔧", end="")  # Test emoji output capability
        print("\r  \r", end="")  # Clear the test character
        return True
    except UnicodeEncodeError:
        return False

# Configure colorama
setup_colorama()
EMOJI_SUPPORT = supports_emoji()

# ANSI color codes
class Colors:
    """
    ANSI color codes and special symbols for terminal output formatting.

    Provides a centralized collection of color codes, formatting options,
    and platform-aware special symbols that fall back to ASCII when
    emoji support is not available.
    """
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    BLACK = '\033[30m'

    # Special symbols - conditional based on emoji support
    CHECKMARK = '✅' if EMOJI_SUPPORT else '[OK]'
    CROSS = '❌' if EMOJI_SUPPORT else '[X]'
    ARROW = '➜' if EMOJI_SUPPORT else '->'
    STAR = '⭐' if EMOJI_SUPPORT else '*'
    LIGHTNING = '⚡' if EMOJI_SUPPORT else '>>'
    CLOCK = '⏱️' if EMOJI_SUPPORT else '[TIME]'
    SEARCH = '🔍' if EMOJI_SUPPORT else '[FIND]'
    TARGET = '🎯' if EMOJI_SUPPORT else '[TARGET]'
    ROCKET = '🚀' if EMOJI_SUPPORT else '[FAST]'
    GEAR = '⚙️' if EMOJI_SUPPORT else '[GEAR]'
    BOOK = '📚' if EMOJI_SUPPORT else '[LIB]'

def install_and_import_mpmath() -> Any:
    """
    Dynamically install and import the mpmath library for high-precision arithmetic.

    Attempts to import mpmath, and if not found, automatically installs it
    using pip before importing. This ensures the benchmark can run even on
    systems where mpmath is not pre-installed.

    Returns:
        module: The imported mpmath module

    Raises:
        subprocess.CalledProcessError: If mpmath installation fails
        ImportError: If mpmath cannot be imported after installation
    """
    try:
        import mpmath
        return mpmath
    except ImportError:
        print(f"{Colors.YELLOW}{'📦' if EMOJI_SUPPORT else '[INSTALL]'} Installing mpmath for high precision...{Colors.END}")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mpmath"])
        import mpmath
        print(f"{Colors.GREEN}{Colors.CHECKMARK} mpmath installed successfully!{Colors.END}")
        return mpmath

def clear_line() -> None:
    """
    Clear the current terminal line for dynamic progress updates.

    Overwrites the current line with spaces and returns cursor to beginning,
    enabling smooth progress indicator updates without creating new lines.
    """
    print("\r" + " " * 120 + "\r", end="", flush=True)

def update_progress_line(text: str, color: str = Colors.CYAN) -> None:
    """
    Update the current line with new progress text.

    Args:
        text: The progress text to display
        color: ANSI color code for the text (default: Colors.CYAN)
    """
    clear_line()
    print(f"\r{color}{text}{Colors.END}", end="", flush=True)

def print_header(title: str, color: str = Colors.BOLD + Colors.CYAN) -> None:
    """
    Print a formatted header with decorative borders.

    Args:
        title: The header text to display
        color: ANSI color code for the header (default: bold cyan)
    """
    width = 60
    print(f"\n{color}{'=' * width}{Colors.END}")
    print(f"{color}{title.center(width)}{Colors.END}")
    print(f"{color}{'=' * width}{Colors.END}")

def format_number(num: int) -> str:
    """
    Format large numbers with thousands separators for readability.

    Args:
        num: The number to format

    Returns:
        str: Formatted number with comma separators (e.g., "1,234,567")
    """
    return f"{num:,}"

def format_time(seconds: float) -> str:
    """
    Format time duration in human-readable format.

    Automatically selects the most appropriate unit (milliseconds, seconds,
    or minutes) based on the duration magnitude.

    Args:
        seconds: Time duration in seconds

    Returns:
        str: Formatted time string (e.g., "123.4ms", "12.345s", "5m 23.1s")
    """
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.3f}s"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"

class Pi69420Benchmark:
    """
    High-performance benchmark for finding "69420" patterns in Pi digits.

    This class implements a sophisticated benchmark that calculates Pi to high
    precision and searches for occurrences of the pattern "69420" using an
    efficient sliding window algorithm. Supports both target-based and time-based
    operation modes with comprehensive performance monitoring.

    Attributes:
        target (str): The pattern to search for ("69420")
        target_occurrences (int): Number of occurrences to find (target mode)
        continuous_seconds (Optional[int]): Time limit in seconds (continuous mode)
        first_known_position (int): Position of first known occurrence (15773)
        is_continuous_mode (bool): Whether running in continuous time mode
    """

    def __init__(self, target_occurrences: int = 3, continuous_seconds: Optional[int] = None):
        """
        Initialize the Pi 69420 benchmark.

        Args:
            target_occurrences: Number of pattern occurrences to find (default: 3)
            continuous_seconds: Time limit for continuous mode (default: None)
        """
        self.target = "69420"
        self.target_occurrences = target_occurrences
        self.continuous_seconds = continuous_seconds
        self.first_known_position = 15773  # First known position of "69420" in Pi
        self.is_continuous_mode = continuous_seconds is not None

    def calculate_pi_precision_needed(self, occurrences: int) -> int:
        """
        Estimate the Pi precision needed to find the target number of occurrences.

        Uses heuristics based on the known distribution of the pattern "69420"
        in Pi's decimal expansion to estimate required precision.

        Args:
            occurrences: Target number of occurrences to find

        Returns:
            int: Estimated precision in decimal digits (capped at 1M)
        """
        # First occurrence is at position 15773
        # Heuristic: each additional occurrence needs approximately 50k digits
        base_precision = 20000  # Base precision for first occurrence
        additional_precision = occurrences * 50000  # Scaling factor per occurrence
        return min(base_precision + additional_precision, 1000000)  # Cap at 1M digits

    def benchmark_with_mpmath(self, occurrences: int) -> Optional[Dict[str, Any]]:
        """
        Execute the main benchmark using mpmath for high-precision Pi calculation.

        This method coordinates the entire benchmark process: precision estimation,
        Pi calculation with timing, and pattern search with performance monitoring.

        Args:
            occurrences: Target number of pattern occurrences to find

        Returns:
            Optional[Dict[str, Any]]: Benchmark results dictionary or None if failed
                Contains: occurrences, digits_processed, calc_time, search_time,
                         total_time, target_reached
        """
        print_header(f"{Colors.TARGET} BENCHMARK: Searching for {occurrences} occurrences of '{self.target}' {Colors.TARGET}")

        mpmath = install_and_import_mpmath()
        precision = self.calculate_pi_precision_needed(occurrences)

        print(f"{Colors.BLUE}{'📊' if EMOJI_SUPPORT else '[INFO]'} Estimated precision needed: {Colors.BOLD}{format_number(precision)} digits{Colors.END}")

        original_dps = mpmath.mp.dps
        try:
            # Configure mpmath precision with buffer for accuracy
            mpmath.mp.dps = precision + 100  # Extra precision to avoid rounding errors

            # Measure Pi calculation time for performance metrics
            print(f"{Colors.YELLOW}{Colors.LIGHTNING} Calculating Pi with high precision...{Colors.END}")
            calc_start = time.time()
            pi_value = mpmath.pi  # Trigger high-precision Pi calculation
            # Convert to string with extra digits for safety margin
            pi_str = mpmath.nstr(pi_value, precision + 10, strip_zeros=False)
            calc_time = time.time() - calc_start

            # Extract decimal digits (everything after the '3.')
            if '.' in pi_str:
                decimal_part = pi_str.split('.')[1]  # Standard format: "3.14159..."
            else:
                decimal_part = pi_str[1:]  # Alternative format: "314159..."

            digits_calculated = len(decimal_part)
            print(f"{Colors.GREEN}{Colors.CHECKMARK} Pi calculated: {Colors.BOLD}{format_number(digits_calculated)} digits{Colors.END} in {Colors.CYAN}{format_time(calc_time)}{Colors.END}")
            print(f"{Colors.MAGENTA}{Colors.LIGHTNING} Calculation rate: {Colors.BOLD}{format_number(int(digits_calculated/calc_time))} digits/sec{Colors.END}")

            # Sequential search
            return self.search_multiple_occurrences(decimal_part, calc_time, occurrences)

        finally:
            mpmath.mp.dps = original_dps

    def search_multiple_occurrences(self, decimal_part: str, calc_time: float, target_occurrences: int) -> Dict[str, Any]:
        """
        Search for multiple pattern occurrences using sliding window algorithm.

        Implements an efficient sliding window search with real-time progress
        monitoring, context display for found patterns, and comprehensive metrics.

        Args:
            decimal_part: Pi decimal digits string to search
            calc_time: Time spent calculating Pi (for metrics)
            target_occurrences: Number of occurrences to find

        Returns:
            Dict[str, Any]: Search results with performance metrics
                - occurrences: List of positions where pattern was found
                - digits_processed: Total digits examined
                - calc_time: Pi calculation time
                - search_time: Pattern search time
                - total_time: Combined time
                - target_reached: Whether target was achieved
        """
        print(f"\n{Colors.SEARCH} {Colors.BOLD}Searching for {target_occurrences} occurrences of '{Colors.YELLOW}{self.target}{Colors.END}{Colors.BOLD}'...{Colors.END}")

        search_start = time.time()
        # Use deque for efficient sliding window operations (O(1) append/pop)
        window = deque(maxlen=5)  # Fixed-size window for "69420" pattern
        occurrences = []  # Store positions where pattern is found
        digits_processed = 0  # Track total digits examined for metrics
        last_progress_update = 0  # Throttle progress updates for performance
        show_initial = True  # Flag to show initial window formation

        # Process each Pi digit sequentially with sliding window
        for i, digit in enumerate(decimal_part):
            window.append(digit)  # Add new digit, automatically removes oldest if full
            digits_processed = i + 1  # Track position in Pi's decimal expansion

            # Display sliding window formation for first 10 digits (educational)
            if show_initial and digits_processed <= 10:
                current_window = ''.join(window)
                if digits_processed == 1:
                    print(f"{Colors.CYAN}Initial window: {Colors.BOLD}{current_window}{Colors.END}", end="", flush=True)
                elif digits_processed <= 10:
                    # Show window growth: "3" -> "31" -> "314" -> "3141" -> "31415"
                    print(f" {Colors.ARROW} {Colors.BOLD}{current_window}{Colors.END}", end="", flush=True)

                # Transition from initial display to main search mode
                if digits_processed == 10:
                    show_initial = False
                    clear_line()  # Remove initial window display
                    print()  # New line before main search output
                    continue  # Skip pattern check for this iteration

            # Pattern matching: check if we have a complete 5-digit window
            if len(window) == 5:
                window_str = ''.join(window)  # Convert deque to string for comparison
                if window_str == self.target:  # Found "69420" pattern
                    # Calculate actual position in Pi (account for window offset)
                    found_position = digits_processed - 4  # Position of first digit in pattern
                    occurrences.append(found_position)

                    clear_line()  # Remove progress indicator
                    print(f"{Colors.GREEN}{Colors.STAR} Occurrence #{len(occurrences)}: '{Colors.BG_YELLOW}{Colors.RED}{Colors.BOLD}{self.target}{Colors.END}' at position {Colors.BOLD}{format_number(found_position)}{Colors.END}")

                    # Create context display: show pattern within surrounding digits
                    context_start = max(0, found_position - 15)  # 15 digits before
                    context_end = min(len(decimal_part), found_position + 20)  # 20 digits after
                    context = decimal_part[context_start:context_end]

                    # Highlight the found pattern within the context
                    highlight_start = found_position - context_start  # Relative position
                    highlight_end = highlight_start + 5  # Length of "69420"
                    highlighted = (context[:highlight_start] +
                                 f"{Colors.BG_GREEN}{Colors.BLACK}{context[highlight_start:highlight_end]}{Colors.END}" +
                                 context[highlight_end:])

                    print(f"{Colors.BLUE}{'📍' if EMOJI_SUPPORT else '[LOC]'} Context at position {found_position}: ...{highlighted}...{Colors.END}")
                    print()  # Extra line to separate from next search

                    # Check if found all (occurrences mode)
                    if not self.is_continuous_mode and len(occurrences) >= target_occurrences:
                        break

            # Check time limit (continuous mode)
            if self.is_continuous_mode:
                elapsed_total = time.time() - search_start
                if elapsed_total >= self.continuous_seconds:
                    clear_line()
                    print(f"\n{Colors.YELLOW}⏰ Time limit reached: {self.continuous_seconds}s{Colors.END}")
                    break

            # Throttled progress updates (every 1000 digits to avoid performance impact)
            if digits_processed % 1000 == 0 and digits_processed > last_progress_update:
                elapsed = time.time() - search_start
                # Calculate current processing rate (digits per second)
                rate = digits_processed / elapsed if elapsed > 0 else 0

                # Format progress message based on operation mode
                if self.is_continuous_mode:
                    # Time-based mode: show countdown and discovery rate
                    remaining_time = max(0, self.continuous_seconds - elapsed)
                    progress_text = (f"{Colors.SEARCH} Processed: {Colors.BOLD}{format_number(digits_processed)}{Colors.END} "
                                   f"| Rate: {Colors.CYAN}{Colors.BOLD}{format_number(int(rate))}{Colors.END} digits/sec "
                                   f"| Found: {Colors.GREEN}{Colors.BOLD}{len(occurrences)}{Colors.END} "
                                   f"| Remaining: {Colors.YELLOW}{Colors.BOLD}{remaining_time:.1f}s{Colors.END}")
                else:
                    # Target-based mode: show progress toward occurrence goal
                    progress_text = (f"{Colors.SEARCH} Processed: {Colors.BOLD}{format_number(digits_processed)}{Colors.END} "
                                   f"| Rate: {Colors.CYAN}{Colors.BOLD}{format_number(int(rate))}{Colors.END} digits/sec "
                                   f"| Found: {Colors.GREEN}{Colors.BOLD}{len(occurrences)}{Colors.END}")

                update_progress_line(progress_text)  # Update same line
                last_progress_update = digits_processed  # Prevent duplicate updates

        search_time = time.time() - search_start
        total_time = calc_time + search_time

        # Clear progress line
        clear_line()

        return {
            'occurrences': occurrences,
            'digits_processed': digits_processed,
            'calc_time': calc_time,
            'search_time': search_time,
            'total_time': total_time,
            'target_reached': len(occurrences) >= target_occurrences
        }

    def print_benchmark_results(self, result: Dict[str, Any]) -> None:
        """
        Display comprehensive benchmark results with formatted metrics.

        Presents a detailed analysis of benchmark performance including timing,
        throughput, efficiency metrics, and position information for found patterns.

        Args:
            result: Dictionary containing benchmark results and metrics
        """
        emoji_title = f"{'📊' if EMOJI_SUPPORT else '[RESULTS]'} BENCHMARK RESULTS {'📊' if EMOJI_SUPPORT else '[RESULTS]'}"
        print_header(emoji_title, Colors.BOLD + Colors.GREEN)

        occurrences = result['occurrences']
        digits = result['digits_processed']
        calc_time = result['calc_time']
        search_time = result['search_time']
        total_time = result['total_time']

        # Benchmark status
        if self.is_continuous_mode:
            # In continuous mode, any occurrence > 0 is success
            is_success = len(occurrences) > 0
            success_icon = f"{Colors.GREEN}{Colors.CHECKMARK}" if is_success else f"{Colors.RED}{Colors.CROSS}"
            success_text = f"{Colors.GREEN}YES" if is_success else f"{Colors.RED}NO"
            target_text = f"{self.continuous_seconds}s continuous"
        else:
            # In normal mode, needs to reach target
            is_success = result['target_reached']
            success_icon = f"{Colors.GREEN}{Colors.CHECKMARK}" if is_success else f"{Colors.RED}{Colors.CROSS}"
            success_text = f"{Colors.GREEN}YES" if is_success else f"{Colors.RED}NO"
            target_text = f"{self.target_occurrences} occurrences"

        print(f"{Colors.TARGET} {Colors.BOLD}Target:{Colors.END} {target_text} of '{Colors.YELLOW}{self.target}{Colors.END}'")
        print(f"{Colors.STAR} {Colors.BOLD}Found:{Colors.END} {Colors.CYAN}{len(occurrences)}{Colors.END} occurrences")
        print(f"{success_icon} {Colors.BOLD}Success:{Colors.END} {success_text}{Colors.END}")
        print()

        # Found positions
        print(f"{Colors.BOLD}{Colors.UNDERLINE}Found positions:{Colors.END}")
        for i, pos in enumerate(occurrences, 1):
            status = f" {Colors.GREEN}(KNOWN){Colors.END}" if pos == self.first_known_position else ""
            print(f"  {Colors.CYAN}#{i}:{Colors.END} position {Colors.BOLD}{format_number(pos)}{Colors.END}{status}")
        print()

        # Time metrics
        print(f"{Colors.BOLD}{Colors.UNDERLINE}{Colors.CLOCK} Time Metrics:{Colors.END}")
        print(f"  {Colors.YELLOW}Pi calculation:{Colors.END} {Colors.CYAN}{format_time(calc_time)}{Colors.END}")
        print(f"  {Colors.YELLOW}Sequential search:{Colors.END} {Colors.CYAN}{format_time(search_time)}{Colors.END}")
        print(f"  {Colors.YELLOW}Total time:{Colors.END} {Colors.BOLD}{Colors.CYAN}{format_time(total_time)}{Colors.END}")
        print()

        # Performance metrics
        print(f"{Colors.BOLD}{Colors.UNDERLINE}{Colors.LIGHTNING} Performance Metrics:{Colors.END}")
        print(f"  {Colors.MAGENTA}Digits processed:{Colors.END} {Colors.BOLD}{format_number(digits)}{Colors.END}")
        print(f"  {Colors.MAGENTA}Digits/second:{Colors.END} {Colors.BOLD}{format_number(int(digits/total_time))}{Colors.END}")
        if calc_time > 0:
            print(f"  {Colors.MAGENTA}Pi calculation/second:{Colors.END} {Colors.BOLD}{1/calc_time:.2f}{Colors.END}")
        else:
            print(f"  {Colors.MAGENTA}Pi calculation/second:{Colors.END} {Colors.BOLD}Real time{Colors.END}")
        print(f"  {Colors.MAGENTA}Search digits/second:{Colors.END} {Colors.BOLD}{format_number(int(digits/search_time))}{Colors.END}")

        if len(occurrences) > 0:
            print(f"  {Colors.MAGENTA}Occurrences/second:{Colors.END} {Colors.BOLD}{len(occurrences)/total_time:.4f}{Colors.END}")
            print(f"  {Colors.MAGENTA}Average time per occurrence:{Colors.END} {Colors.BOLD}{format_time(total_time/len(occurrences))}{Colors.END}")
        else:
            print(f"  {Colors.MAGENTA}Occurrences/second:{Colors.END} {Colors.BOLD}0.0000{Colors.END}")
            print(f"  {Colors.MAGENTA}Average time per occurrence:{Colors.END} {Colors.BOLD}N/A{Colors.END}")

        # Efficiency metrics with color-coded performance indicators
        if len(occurrences) > 0:
            if self.is_continuous_mode:
                # Continuous mode: measure pattern discovery rate
                rate_per_sec = len(occurrences) / self.continuous_seconds
                # Color coding: Green (excellent) >= 1/sec, Yellow (good) >= 0.5/sec, Cyan (normal) < 0.5/sec
                efficiency_color = Colors.GREEN if rate_per_sec >= 1 else Colors.YELLOW if rate_per_sec >= 0.5 else Colors.CYAN
                print(f"  {Colors.MAGENTA}Discovery rate:{Colors.END} {efficiency_color}{Colors.BOLD}{rate_per_sec:.2f} occurrences/second{Colors.END}")
            else:
                # Target mode: measure goal completion percentage
                efficiency = (len(occurrences) / self.target_occurrences) * 100
                # Color coding: Green (complete) >= 100%, Yellow (partial) >= 80%, Red (low) < 80%
                efficiency_color = Colors.GREEN if efficiency >= 100 else Colors.YELLOW if efficiency >= 80 else Colors.RED
                print(f"  {Colors.MAGENTA}Efficiency:{Colors.END} {efficiency_color}{Colors.BOLD}{efficiency:.1f}%{Colors.END}")

        print(f"\n{Colors.CYAN}{'=' * 70}{Colors.END}")

    def run_benchmark(self, occurrences: int) -> bool:
        """
        Execute a complete target-based benchmark run.

        Orchestrates the full benchmark process from start to finish, including
        timing, error handling, and result presentation.

        Args:
            occurrences: Target number of pattern occurrences to find

        Returns:
            bool: True if benchmark completed successfully, False otherwise
        """
        start_time = time.time()

        print_header(f"{Colors.TARGET} Pi 69420 Benchmark - Performance Tester {Colors.TARGET}", Colors.BOLD + Colors.MAGENTA)
        print(f"{Colors.BLUE}{Colors.GEAR} Algorithm:{Colors.END} Sequential calculation + sliding window")
        print(f"{Colors.BLUE}{Colors.BOOK} Library:{Colors.END} mpmath (high precision)")
        print(f"{Colors.BLUE}{Colors.SEARCH} Window:{Colors.END} 5 sliding digits")

        try:
            result = self.benchmark_with_mpmath(occurrences)

            if result:
                self.print_benchmark_results(result)
                return True
            else:
                print(f"{Colors.RED}{Colors.CROSS} Error: Benchmark failed{Colors.END}")
                return False

        except Exception as e:
            print(f"{Colors.RED}{Colors.CROSS} Error during benchmark: {e}{Colors.END}")
            return False

        finally:
            total_benchmark_time = time.time() - start_time
            print(f"\n{Colors.CLOCK} {Colors.BOLD}Total benchmark time:{Colors.END} {Colors.CYAN}{format_time(total_benchmark_time)}{Colors.END}")

    def run_continuous_benchmark(self, seconds: int) -> bool:
        """
        Execute a continuous time-based benchmark run.

        Runs the benchmark for a specified duration, calculating Pi digits
        incrementally and searching for patterns in real-time.

        Args:
            seconds: Duration to run the benchmark

        Returns:
            bool: True if benchmark completed successfully, False otherwise
        """
        start_time = time.time()

        print_header(f"{Colors.TARGET} Pi 69420 Benchmark - Continuous Mode {Colors.TARGET}", Colors.BOLD + Colors.YELLOW)
        print(f"{Colors.BLUE}{Colors.GEAR} Algorithm:{Colors.END} Incremental digit-by-digit calculation")
        print(f"{Colors.BLUE}{Colors.BOOK} Library:{Colors.END} mpmath (incremental precision)")
        print(f"{Colors.BLUE}{Colors.SEARCH} Window:{Colors.END} 5 sliding digits in real time")
        print(f"{Colors.BLUE}{Colors.CLOCK} Duration:{Colors.END} {Colors.BOLD}{seconds} seconds{Colors.END}")

        try:
            # Sequential real-time calculation using incremental mpmath
            calc_start = time.time()

            print(f"\n{Colors.YELLOW}{Colors.LIGHTNING} Calculating Pi digit-by-digit for {seconds} seconds...{Colors.END}")

            result = self.continuous_mpmath_search(seconds, calc_start)

            if result:
                self.print_benchmark_results(result)
                return True
            else:
                print(f"{Colors.RED}{Colors.CROSS} Error: Continuous benchmark failed{Colors.END}")
                return False

        except Exception as e:
            print(f"{Colors.RED}{Colors.CROSS} Error during continuous benchmark: {e}{Colors.END}")
            return False

        finally:
            total_benchmark_time = time.time() - start_time
            print(f"\n{Colors.CLOCK} {Colors.BOLD}Total continuous benchmark time:{Colors.END} {Colors.CYAN}{format_time(total_benchmark_time)}{Colors.END}")

    def continuous_mpmath_search(self, time_limit: int, start_time: float) -> Optional[Dict[str, Any]]:
        """
        Perform real-time Pi calculation and pattern search with time constraints.

        Implements incremental precision expansion to calculate Pi digits on-demand
        while simultaneously searching for patterns within the specified time limit.

        Args:
            time_limit: Maximum time to run the search (seconds)
            start_time: Benchmark start timestamp

        Returns:
            Optional[Dict[str, Any]]: Search results or None if failed
        """
        print(f"\n{Colors.SEARCH} {Colors.BOLD}Calculating Pi in real time with mpmath...{Colors.END}")

        mpmath = install_and_import_mpmath()
        original_dps = mpmath.mp.dps

        try:
            window = deque(maxlen=5)
            occurrences = []
            digits_processed = 0
            last_progress_update = 0
            show_initial = True
            current_precision = 50  # Start with 50 digits

            # Buffer to store already calculated digits
            pi_digits_buffer = ""

            # Main real-time calculation and search loop
            while True:
                # Time limit enforcement for continuous mode
                elapsed = time.time() - start_time
                if elapsed >= time_limit:
                    clear_line()
                    print(f"\n{Colors.YELLOW}{'⏰' if EMOJI_SUPPORT else '[TIME]'} Time limit reached: {time_limit}s{Colors.END}")
                    break

                # Dynamic precision expansion: calculate more Pi digits when buffer runs low
                if digits_processed >= len(pi_digits_buffer) - 10:  # Safety margin of 10 digits
                    current_precision += 200  # Incremental precision increase for efficiency
                    mpmath.mp.dps = current_precision  # Update mpmath precision setting

                    calc_start_partial = time.time()
                    pi_value = mpmath.pi
                    pi_str = mpmath.nstr(pi_value, current_precision - 10, strip_zeros=False)
                    calc_time_partial = time.time() - calc_start_partial

                    if '.' in pi_str:
                        new_decimal_part = pi_str.split('.')[1]
                    else:
                        new_decimal_part = pi_str[1:]

                    # Buffer management: only update if we got more digits
                    if len(new_decimal_part) > len(pi_digits_buffer):
                        pi_digits_buffer = new_decimal_part  # Replace with expanded calculation

                    # Progress feedback: show precision expansion (skip first iteration)
                    if digits_processed > 0:
                        clear_line()
                        print(f"{Colors.YELLOW}{'🔄' if EMOJI_SUPPORT else '[CALC]'} Expanding precision to {current_precision} digits... ({calc_time_partial:.2f}s){Colors.END}")

                # If we have no more digits, exit loop
                if digits_processed >= len(pi_digits_buffer):
                    break

                # Process next digit
                digit = pi_digits_buffer[digits_processed]
                window.append(digit)
                digits_processed += 1

                # Show initial progress
                if show_initial and digits_processed <= 10:
                    current_window = ''.join(window)
                    if digits_processed == 1:
                        print(f"{Colors.CYAN}Pi in real time: {Colors.BOLD}{current_window}{Colors.END}", end="", flush=True)
                    elif digits_processed <= 10:
                        print(f" {Colors.ARROW} {Colors.BOLD}{current_window}{Colors.END}", end="", flush=True)

                    if digits_processed == 10:
                        show_initial = False
                        clear_line()
                        print()
                        continue

                # Check if found an occurrence
                if len(window) == 5:
                    window_str = ''.join(window)
                    if window_str == self.target:
                        found_position = digits_processed - 4
                        occurrences.append(found_position)

                        clear_line()
                        print(f"{Colors.GREEN}{Colors.STAR} Occurrence #{len(occurrences)}: '{Colors.BG_YELLOW}{Colors.RED}{Colors.BOLD}{self.target}{Colors.END}' at position {Colors.BOLD}{format_number(found_position)}{Colors.END}")

                        # Show context with buffer digits
                        context_start = max(0, found_position - 15)
                        context_end = min(len(pi_digits_buffer), found_position + 20)
                        if context_end <= len(pi_digits_buffer):
                            context = pi_digits_buffer[context_start:context_end]
                            highlight_start = found_position - context_start
                            highlight_end = highlight_start + 5
                            highlighted = (context[:highlight_start] +
                                         f"{Colors.BG_GREEN}{Colors.BLACK}{context[highlight_start:highlight_end]}{Colors.END}" +
                                         context[highlight_end:])
                            print(f"{Colors.BLUE}{'📍' if EMOJI_SUPPORT else '[LOC]'} Context at position {found_position}: ...{highlighted}...{Colors.END}")
                        print()

                # Dynamic progress every 250 digits (more frequent in continuous mode)
                if digits_processed % 250 == 0 and digits_processed > last_progress_update:
                    elapsed = time.time() - start_time
                    remaining_time = max(0, time_limit - elapsed)
                    rate = digits_processed / elapsed if elapsed > 0 else 0

                    progress_text = (f"{Colors.SEARCH} Calculated: {Colors.BOLD}{format_number(digits_processed)}{Colors.END} digits "
                                   f"| Rate: {Colors.CYAN}{Colors.BOLD}{format_number(int(rate))}{Colors.END} digits/sec "
                                   f"| Found: {Colors.GREEN}{Colors.BOLD}{len(occurrences)}{Colors.END} "
                                   f"| Remaining: {Colors.YELLOW}{Colors.BOLD}{remaining_time:.1f}s{Colors.END}")

                    update_progress_line(progress_text)
                    last_progress_update = digits_processed

                # Controlled processing rate: prevent CPU overload and simulate realistic timing
                import time as time_module
                time_module.sleep(0.0005)  # 0.5ms per digit (2000 digits/second max rate)

            total_time = time.time() - start_time
            clear_line()

            return {
                'occurrences': occurrences,
                'digits_processed': digits_processed,
                'calc_time': 0,  # Calculation time is distributed
                'search_time': total_time,
                'total_time': total_time,
                'target_reached': len(occurrences) >= self.target_occurrences
            }

        finally:
            mpmath.mp.dps = original_dps

def main() -> int:
    """
    Main entry point for the Pi 69420 Benchmark application.

    Handles command-line argument parsing, input validation, and benchmark
    execution coordination. Supports both target-based and time-based modes.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}{Colors.CYAN}Pi 69420 Benchmark{Colors.END} - Finds multiple occurrences of '69420' in Pi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.BOLD}{Colors.GREEN}Examples:{Colors.END}
  {Colors.CYAN}python pi_69420.py{Colors.END}              # Search for 3 occurrences (default)
  {Colors.CYAN}python pi_69420.py -n 1{Colors.END}         # Search for only 1 occurrence
  {Colors.CYAN}python pi_69420.py -n 5{Colors.END}         # Search for 5 occurrences
  {Colors.CYAN}python pi_69420.py --count 10{Colors.END}   # Search for 10 occurrences
  {Colors.CYAN}python pi_69420.py -c 10{Colors.END}        # Continuous mode for 10 seconds
  {Colors.CYAN}python pi_69420.py --continuous 30{Colors.END} # Continuous mode for 30 seconds
        """
    )

    parser.add_argument(
        '-n', '--count',
        type=int,
        default=3,
        metavar='N',
        help='Number of "69420" occurrences to find (default: 3, maximum: 250)'
    )

    parser.add_argument(
        '-c', '--continuous',
        type=int,
        metavar='SECONDS',
        help='Continuous mode: search for X seconds instead of N occurrences'
    )

    args = parser.parse_args()

    # Display application banner and version information
    print(f"{Colors.BOLD}{Colors.CYAN}Pi 69420 Benchmark v1.0{Colors.END}")
    print(f"{Colors.BLUE}High-precision pattern search in Pi digits{Colors.END}\n")

    # Input validation with reasonable limits to prevent system overload
    if args.continuous and args.continuous < 1:
        print(f"{Colors.RED}{Colors.CROSS} Error: Continuous time must be at least 1 second{Colors.END}")
        return 1

    if args.continuous and args.continuous > 3600:  # 1 hour limit for safety
        print(f"{Colors.RED}{Colors.CROSS} Error: Maximum continuous time is 3600 seconds (1 hour){Colors.END}")
        return 1

    if not args.continuous:
        if args.count < 1:
            print(f"{Colors.RED}{Colors.CROSS} Error: Number of occurrences must be at least 1{Colors.END}")
            return 1

        if args.count > 250:  # Reasonable upper limit (would require ~12.5M digits)
            print(f"{Colors.RED}{Colors.CROSS} Error: Maximum number of occurrences is 250{Colors.END}")
            return 1

    # Run benchmark
    if args.continuous:
        benchmark = Pi69420Benchmark(continuous_seconds=args.continuous)
        success = benchmark.run_continuous_benchmark(args.continuous)
    else:
        benchmark = Pi69420Benchmark(args.count)
        success = benchmark.run_benchmark(args.count)

    if success:
        print(f"\n{Colors.GREEN}{Colors.CHECKMARK} Benchmark completed successfully!{Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.CROSS} Benchmark failed!{Colors.END}")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())