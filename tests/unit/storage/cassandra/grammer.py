from pyparsing import Literal, CaselessLiteral, Word, Upcase, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword


# CQL Command templates
CREATE_KEYSPACE_CMD = 'CREATE KEYSPACE'
USE_KEYSPACE_CMD = 'USE'
SELECT_CMD = 'SELECT'
INSERT_CMD = 'INSERT'
UPDATE_CMD = 'UPDATE'
DELETE_CMD = 'DELETE'


# base constructs
and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)
in_ = Keyword("in", caseless=True)

E = CaselessLiteral("E")
binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
arithSign = Word("+-",exact=1)
realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) )  |
                                                         ( "." + Word(nums) ) ) +
            Optional( E + Optional(arithSign) + Word(nums) ) )
intNum = Combine( Optional(arithSign) + Word( nums ) +
            Optional( E + Optional("+") + Word(nums) ) )


# tokens
selectToken = Keyword("select", caseless=True)
fromToken   = Keyword("from", caseless=True)


# forwards
whereExpression = Forward()
selectStmt = Forward()


# block constructs
ident          = Word( alphas, alphanums + "_$" ).setName("identifier")
columnName     = Upcase( delimitedList( ident, ".", combine=True ) )
columnNameList = Group( delimitedList( columnName ) )
tableName      = Upcase( delimitedList( ident, ".", combine=True ) )
tableNameList  = Group( delimitedList( tableName ) )

columnRval = realNum | intNum | quotedString | columnName # need to add support for alg expressions
whereCondition = Group( columnName + binop + columnRval )
whereExpression << whereCondition + ZeroOrMore( ( and_ | or_ ) + whereExpression )


# grammer
selectStmt      << ( selectToken +
                   ( '*' | columnNameList ).setResultsName( "columns" ) +
                   fromToken +
                   tableNameList.setResultsName( "tables" ) +
                   Optional( Group( CaselessLiteral("where") + whereExpression ), "" ).setResultsName("where") )
