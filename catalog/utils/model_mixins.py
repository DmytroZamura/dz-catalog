from django.db import models


class UpdateQtyMixin(models.Model):
    class Meta:
        abstract = True

    def update_events_qty(self, field_name, qty):
        """
        This function is for tables which manage event qty field.
        :param field_name:
        :param qty:
        """
        try:
            if self is not None:
                field = self.__getattribute__(field_name)
                field += qty
                if field >= 0:
                    self.__setattr__(field_name, field)
                    self.save()
        except self.DoesNotExist:
            pass
