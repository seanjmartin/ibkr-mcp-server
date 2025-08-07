# IBKR Subscription Model Example
# This shows how to replace hanging API calls with working subscription model

import asyncio
from typing import List, Dict

class IBKRClientWithSubscription:
    """Example implementation using subscription model instead of hanging API calls"""
    
    def __init__(self):
        self.ib = None  # IBKR client
        self.current_account = None
        self._subscriptions_active = set()  # Track active subscriptions
    
    async def get_account_summary(self, account: str = None) -> List[Dict]:
        """
        NEW IMPLEMENTATION: Uses subscription model instead of reqAccountSummaryAsync()
        """
        account = account or self.current_account
        
        # Start subscription if not already active
        if account not in self._subscriptions_active:
            print(f"[DEBUG] Starting account subscription for {account}")
            self.ib.reqAccountUpdates(True, account)
            self._subscriptions_active.add(account)
            
            # Wait for initial data to arrive
            await asyncio.sleep(3.0)
        
        # Get cached account data (instant - no API call)
        account_values = self.ib.accountValues()
        
        # Convert to same format as old API
        summary = []
        for av in account_values:
            if av.account == account:  # Filter by account
                summary.append({
                    'tag': av.tag,
                    'value': av.value, 
                    'currency': av.currency,
                    'account': av.account
                })
        
        return summary
    
    async def get_portfolio(self, account: str = None) -> List[Dict]:
        """
        NEW IMPLEMENTATION: Uses subscription model instead of reqPositionsAsync()  
        """
        account = account or self.current_account
        
        # Start subscription if not already active (same subscription serves both!)
        if account not in self._subscriptions_active:
            print(f"[DEBUG] Starting account subscription for {account}")
            self.ib.reqAccountUpdates(True, account)
            self._subscriptions_active.add(account)
            
            # Wait for initial data to arrive
            await asyncio.sleep(3.0)
        
        # Get cached portfolio data (instant - no API call)
        portfolio_items = self.ib.portfolio()
        
        # Convert to same format as old API
        portfolio = []
        for item in portfolio_items:
            if item.account == account:  # Filter by account
                portfolio.append({
                    'symbol': item.contract.symbol,
                    'exchange': item.contract.exchange,
                    'currency': item.contract.currency,
                    'position': item.position,
                    'average_cost': item.averageCost,
                    'market_price': item.marketPrice,
                    'market_value': item.marketValue,
                    'unrealized_pnl': item.unrealizedPNL,
                    'realized_pnl': item.realizedPNL,
                    'account': item.account
                })
        
        return portfolio
    
    async def cleanup_subscriptions(self):
        """Stop all active subscriptions"""
        for account in self._subscriptions_active:
            print(f"[DEBUG] Stopping account subscription for {account}")
            self.ib.reqAccountUpdates(False, account)
        
        self._subscriptions_active.clear()


# COMPARISON: Old vs New

class OldApproach:
    """OLD APPROACH - Hangs indefinitely"""
    
    async def get_account_summary(self):
        # ❌ This hangs and never returns
        account_values = await self.ib.reqAccountSummaryAsync()
        return account_values
    
    async def get_portfolio(self):
        # ❌ This hangs and never returns  
        positions = await self.ib.reqPositionsAsync()
        return positions


class NewApproach:
    """NEW APPROACH - Works reliably"""
    
    async def get_account_summary(self):
        # ✅ Start subscription (returns immediately)
        self.ib.reqAccountUpdates(True, account)
        await asyncio.sleep(2.0)  # Wait for data
        
        # ✅ Get cached data (instant)
        account_values = self.ib.accountValues()
        return self._format_account_data(account_values)
    
    async def get_portfolio(self):
        # ✅ Same subscription provides portfolio data too!
        # No additional API call needed if subscription already active
        portfolio_items = self.ib.portfolio()
        return self._format_portfolio_data(portfolio_items)


# KEY DIFFERENCES:

# OLD: Request → Wait → Hang Forever
# NEW: Subscribe → Stream → Cache → Access

# OLD: Each call makes new API request  
# NEW: One subscription serves multiple data needs

# OLD: Static snapshot data
# NEW: Live streaming data with real-time updates

# OLD: Hangs in paper trading
# NEW: Works reliably in all environments
