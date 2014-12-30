# -*- coding: utf-8 -*-

#   Copyright (c) 2010-2014, MIT Probabilistic Computing Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from collections import namedtuple

QueryAction = namedtuple('QueryAction', [
    'action',                   # QACT_*
    'query',                    # Select or Infer or ... XXX
])
QACT_FREQ = 'freq'
QACT_HIST = 'hist'
QACT_SUMMARIZE = 'summarize'
QACT_PLOT = 'plot'

Select = namedtuple('Select', [
    'quantifier',               # SELQUANT_*
    'output',                   # SelCols or SelBQL*
    'tables',                   # [XXX name or Query*]
    'condition',                # Exp*
    'group',                    # [Exp*]
    'order',                    # [Ord]
    'limit',                    # Lim or None (unlimited)
])

SELQUANT_DISTINCT = 'distinct'
SELQUANT_ALL = 'ALL'

SelCols = namedtuple('SelCols', [
    'columns',                  # SelCol
])
SelCol = namedtuple('SelCol', [
    'value',                    # SelColTab | SelColExp
    'name',                     # XXX name
])
SelColAll = namedtuple('SelColAll', [
    'table',                    # XXX name
])
SelColExp = namedtuple('SelColExp', [
    'expression',               # Exp*
])

SelBQLPredProb = namedtuple('SelBQLPredProb', ['column'])
SelBQLProb = namedtuple('SelBQLProb', ['column', 'value'])
SelBQLTypRow = namedtuple('SelBQLTypRow', []) # XXX Accept rowid?
SelBQLTypCol = namedtuple('SelBQLTypCol', ['column'])
SelBQLSim = namedtuple('SelBQLSim', ['rowid', 'column_lists'])
SelBQLDepProb = namedtuple('SelBQLDepProb', ['column1', 'column2'])
SelBQLMutInf = namedtuple('SelBQLMutInf', ['column1', 'column2'])
SelBQLCorrel = namedtuple('SelBQLCorrel', ['column1', 'column2'])

ColListAll = namedtuple('ColListAll', [])
ColListLit = namedtuple('ColListLit', ['columns'])
ColListSub = namedtuple('ColListSub', ['query']) # subquery
ColListSav = namedtuple('ColListSav', ['name']) # saved

Ord = namedtuple('Ord', ['expression', 'sense'])
ORD_ASC = True
ORD_DESC = False

Lim = namedtuple('Lim', ['limit', 'offset'])

ExpLit = namedtuple('ExpLit', ['value'])
ExpCol = namedtuple('ExpCol', ['table', 'column'])

LitNull = namedtuple('LitNull', ['value'])
LitInt = namedtuple('LitInt', ['value'])
LitFloat = namedtuple('LitFloat', ['value'])
LitString = namedtuple('LitString', ['value'])
