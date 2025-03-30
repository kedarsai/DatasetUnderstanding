-- Create DU_Datasets table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[DU_Datasets]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[DU_Datasets](
        [DatasetID] [int] IDENTITY(1,1) NOT NULL,
        [DatasetName] [nvarchar](100) NOT NULL,
        [Description] [nvarchar](500) NULL,
        [CreatedDate] [datetime] NOT NULL DEFAULT GETDATE(),
        [CreatedBy] [nvarchar](100) NOT NULL,
        [ViewName] [nvarchar](100) NOT NULL,
        [JoinConditions] [nvarchar](max) NOT NULL,
        [Tables] [nvarchar](max) NOT NULL,
        [DatabaseName] [nvarchar](100) NOT NULL,
        [ServerName] [nvarchar](100) NOT NULL,
        CONSTRAINT [PK_DU_Datasets] PRIMARY KEY CLUSTERED ([DatasetID] ASC)
    )
END

-- Add indexes for better performance
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_DU_Datasets_DatasetName' AND object_id = OBJECT_ID('DU_Datasets'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_DU_Datasets_DatasetName] ON [dbo].[DU_Datasets]([DatasetName])
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_DU_Datasets_CreatedDate' AND object_id = OBJECT_ID('DU_Datasets'))
BEGIN
    CREATE NONCLUSTERED INDEX [IX_DU_Datasets_CreatedDate] ON [dbo].[DU_Datasets]([CreatedDate])
END 